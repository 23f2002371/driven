"""Integration tests for the authentication endpoints.

Each test is self-contained and creates its own data via the API or the
``db_session`` fixture, never relying on test execution order.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User

API = "/api/auth"

# --------------------------------------------------------------- Registration
def test_register_success(client: TestClient) -> None:
    payload = {
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "password": "securepass123",
    }

    response = client.post(f"{API}/register", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == payload["email"]
    assert body["full_name"] == payload["full_name"]
    assert body["role"] == "student"
    assert "password" not in body


def test_register_duplicate_email(client: TestClient, db_session: Session) -> None:
    client.post(
        f"{API}/register",
        json={
            "full_name": "First User",
            "email": "dup@example.com",
            "password": "securepass123",
        },
    )

    response = client.post(
        f"{API}/register",
        json={
            "full_name": "Second User",
            "email": "dup@example.com",
            "password": "securepass123",
        },
    )

    assert response.status_code == 409


def test_register_invalid_email(client: TestClient) -> None:
    response = client.post(
        f"{API}/register",
        json={
            "full_name": "Jane Doe",
            "email": "not-an-email",
            "password": "securepass123",
        },
    )

    assert response.status_code == 422


def test_register_missing_required_field(client: TestClient) -> None:
    response = client.post(
        f"{API}/register",
        json={
            "email": "jane@example.com",
            "password": "securepass123",
        },
    )

    assert response.status_code == 422


def test_register_short_password(client: TestClient) -> None:
    response = client.post(
        f"{API}/register",
        json={
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "password": "short",
        },
    )

    assert response.status_code == 422


# -------------------------------------------------------------------- Login
def test_login_success(client: TestClient, db_session: Session) -> None:
    user = User(
        full_name="Jane Doe",
        email="jane@example.com",
        password_hash=get_password_hash("securepass123"),
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        f"{API}/login",
        json={"email": "jane@example.com", "password": "securepass123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password(client: TestClient, db_session: Session) -> None:
    user = User(
        full_name="Jane Doe",
        email="jane@example.com",
        password_hash=get_password_hash("securepass123"),
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        f"{API}/login",
        json={"email": "jane@example.com", "password": "wrongpass123"},
    )

    assert response.status_code == 401


def test_login_unknown_email(client: TestClient) -> None:
    response = client.post(
        f"{API}/login",
        json={"email": "ghost@example.com", "password": "securepass123"},
    )

    assert response.status_code == 401


def test_login_oauth_only_user(client: TestClient, db_session: Session) -> None:
    user = User(
        full_name="OAuth User",
        email="oauth@example.com",
        password_hash=None,
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        f"{API}/login",
        json={"email": "oauth@example.com", "password": "anything"},
    )

    assert response.status_code == 401


def test_login_missing_credentials(client: TestClient) -> None:
    response = client.post(f"{API}/login", json={})

    assert response.status_code == 422


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"email": "jane@example.com"},
        {"password": "securepass123"},
    ],
)
def test_register_missing_credentials_variants(
    client: TestClient, payload: dict
) -> None:
    response = client.post(f"{API}/register", json=payload)

    assert response.status_code == 422
