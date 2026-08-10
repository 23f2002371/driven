"""Fixtures that require a live test database.

Only integration tests request the database/HTTP fixtures, so the SQLite
schema is created and reset exclusively here - unit tests remain disk-free.
"""

from __future__ import annotations

from collections.abc import Generator

import pytest
from sqlalchemy import Engine

from app.core.database import Base


@pytest.fixture(autouse=True)
def _reset_database(engine: Engine) -> Generator:
    """Reset the schema before every test so tests never share state."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield