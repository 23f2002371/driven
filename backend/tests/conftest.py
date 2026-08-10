"""Shared pytest configuration and fixtures.

- Sets up a dedicated SQLite test database (``test.db``) that is created before
  the test session and dropped afterwards, so no test ever touches the
  development/production PostgreSQL database.
- Overrides the FastAPI ``get_db`` dependency with the test session.
- Provides a ``TestClient`` and database session fixtures.
- Provides authentication helpers (user creation + JWT headers).
- Emits a JSON results log in ``reports/results_log.json`` after the run.
"""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

# Configure the app environment *before* importing any app module so that
# ``app.core.config.settings`` reads a safe, hermetic test configuration.
# Note: DATABASE_URL is left to the app's own config; the app engine is never
# connected to because ``get_db`` is overridden with the in-memory test engine.
os.environ["SECRET_KEY"] = "test-secret-key-for-automated-tests"
os.environ["ALGORITHM"] = "HS256"
os.environ["PROJECT_NAME"] = "Test API"
os.environ["API_STR"] = "/api"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

from app.core.database import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models.user import User
from app.utils.enums import UserRole


@pytest.fixture(scope="session")
def engine(tmp_path_factory: pytest.TempPathFactory) -> Generator:
    """Create the isolated SQLite engine, dropping the schema at session end.

    The ``test.db`` file lives in pytest's native temp directory (never the
    development database) and is removed once the session finishes.
    """
    db_path = tmp_path_factory.mktemp("testdb") / "test.db"
    test_engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture()
def db_session(engine: Engine) -> Generator[Session]:
    """A fresh SQLAlchemy session bound to the test database."""
    session = Session(engine)
    yield session
    session.close()


@pytest.fixture()
def client(engine: Engine) -> Generator[TestClient]:
    """A TestClient whose ``get_db`` dependency points at the test database."""

    def override_get_db() -> Generator[Session]:
        db = Session(engine)
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def student(db_session: Session) -> User:
    return _create_user(db_session, role=UserRole.STUDENT, email="student@example.com")


@pytest.fixture()
def club_admin(db_session: Session) -> User:
    return _create_user(db_session, role=UserRole.CLUB_ADMIN, email="admin@example.com")


@pytest.fixture()
def lab_admin(db_session: Session) -> User:
    return _create_user(db_session, role=UserRole.LAB_ADMIN, email="labadmin@example.com")


def _create_user(
    db: Session,
    *,
    role: UserRole,
    email: str,
    password: str = "testpassword123",
) -> User:
    """Insert a user with a known password into the test database."""
    user = User(
        full_name="Test User",
        email=email,
        password_hash=get_password_hash(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def auth_headers(user: User) -> dict[str, str]:
    """A valid Bearer Authorization header for the given user."""
    token = create_access_token(subject=user.id)
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------- Reporting
_TEST_RESULTS: list[dict] = []
_TEST_ACTUALS: dict[str, str] = {}


def record_actual(actual: str) -> None:
    """Record the actual output text of the calling test.

    Keyed by the calling test function name so the matrix generator can render
    a real ``Actual Output`` cell even when the test fails.
    """
    frame = sys._getframe(1)
    _TEST_ACTUALS[frame.f_code.co_name] = actual


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        _TEST_RESULTS.append(
            {
                "test": report.nodeid,
                "outcome": report.outcome,
                "error": str(report.longrepr) if report.failed else None,
            }
        )


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session: pytest.Session, exitstatus: int):
    reports_dir = Path(__file__).resolve().parent / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "results_log.json").write_text(
        json.dumps(_TEST_RESULTS, indent=2), encoding="utf-8"
    )
    (reports_dir / "actual_outputs.json").write_text(
        json.dumps(_TEST_ACTUALS, indent=2), encoding="utf-8"
    )