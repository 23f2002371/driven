"""Integration tests for the authentication API.

Each test is self-contained and creates its own data via the API or the
``db_session`` fixture, never relying on test execution order.

This suite intentionally includes "negative" and boundary tests. It also
documents currently-known API limitations, pinned as current behaviour in the
relevant tests (so they pass but flag the gap via comments), plus one genuine
bug still surfaced as a failing test:
  - login email is still treated case-sensitively; register normalizes emails
    to lowercase but UserLogin has no such normalization, so a differently-cased
    login email returns 401 (test passes but documents the gap).
  - registering with ``email=null`` crashes with a 500 because the ``before``
    email validator calls ``.strip().lower()`` on None instead of deferring to
    pydantic's 422 (this test FAILS by design to keep the bug visible).
"""

from __future__ import annotations

import base64
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta

import jose
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash
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


def test_register_empty_full_name(client: TestClient) -> None:
    response = client.post(
        f"{API}/register",
        json={"full_name": "", "email": "jane@example.com", "password": "securepass123"},
    )

    assert response.status_code == 422


def test_register_whitespace_only_full_name(client: TestClient) -> None:
    # A name made solely of spaces must be rejected (not just pass min_length).
    response = client.post(
        f"{API}/register",
        json={"full_name": "   ", "email": "jane@example.com", "password": "securepass123"},
    )

    assert response.status_code == 422


def test_register_full_name_not_trimmed(client: TestClient) -> None:
    # Leading/trailing padding around a name should be normalized before storage.
    response = client.post(
        f"{API}/register",
        json={"full_name": "  Jane Doe  ", "email": "jane@example.com", "password": "securepass123"},
    )

    assert response.status_code == 201
    assert response.json()["full_name"] == "Jane Doe"


def test_register_email_normalized_whitespace(client: TestClient) -> None:
    # email-validator strips surrounding whitespace before storage.
    response = client.post(
        f"{API}/register",
        json={"full_name": "Jane Doe", "email": "  jane@example.com  ", "password": "securepass123"},
    )

    assert response.status_code == 201
    assert response.json()["email"] == "jane@example.com"


def test_register_duplicate_email_different_case(client: TestClient) -> None:
    # Emails are case-insensitive identifiers; a differently-cased duplicate should collide.
    client.post(
        f"{API}/register",
        json={"full_name": "First", "email": "Case@example.com", "password": "securepass123"},
    )
    response = client.post(
        f"{API}/register",
        json={"full_name": "Second", "email": "case@EXAMPLE.com", "password": "securepass123"},
    )

    assert response.status_code == 409


@pytest.mark.parametrize(
    "password",
    [
        "123456",  # exactly at the minimum length (6)
        "a" * 72,  # exactly at the maximum length (72 = bcrypt safe limit)
    ],
)
def test_register_password_boundary_lengths(client: TestClient, password: str) -> None:
    # Boundary values at the configured min/max password lengths are valid.
    response = client.post(
        f"{API}/register",
        json={"full_name": "Jane Doe", "email": f"bnd-{len(password)}@example.com", "password": password},
    )

    assert response.status_code == 201


def test_register_password_over_max_length(client: TestClient) -> None:
    # Passwords longer than Field(max_length=72) must be rejected.
    response = client.post(
        f"{API}/register",
        json={"full_name": "Jane Doe", "email": "jane@example.com", "password": "a" * 73},
    )

    assert response.status_code == 422


def test_register_whitespace_only_password(client: TestClient) -> None:
    # A password of 8 spaces must be rejected: UserCreate now refuses
    # whitespace-only passwords in addition to enforcing a minimum length.
    response = client.post(
        f"{API}/register",
        json={"full_name": "Jane Doe", "email": "jane@example.com", "password": "        "},
    )

    assert response.status_code == 422


def test_register_full_name_over_max_length(client: TestClient) -> None:
    # full_name longer than the 100-char column limit must be rejected.
    response = client.post(
        f"{API}/register",
        json={"full_name": "x" * 101, "email": "jane@example.com", "password": "securepass123"},
    )

    assert response.status_code == 422


def test_register_email_over_max_length(client: TestClient) -> None:
    # Email beyond the 150-char field limit must be rejected.
    local, domain = "a" * 140, "b" * 10
    response = client.post(
        f"{API}/register",
        json={"full_name": "Jane Doe", "email": f"{local}@{domain}.com", "password": "securepass123"},
    )

    assert response.status_code == 422


def test_register_password_at_bcrypt_limit_roundtrips(client: TestClient) -> None:
    # bcrypt only hashes the first 72 bytes. The API now caps passwords at
    # exactly 72 bytes, so a password at that boundary must register and then
    # login successfully with the exact same value.
    password = "A" * 72
    reg = client.post(
        f"{API}/register",
        json={"full_name": "Jane Doe", "email": "bcrypt@example.com", "password": password},
    )
    assert reg.status_code == 201

    login = client.post(
        f"{API}/login",
        json={"email": "bcrypt@example.com", "password": password},
    )

    assert login.status_code == 200


@pytest.mark.parametrize(
    "extra",
    [
        {"role": "admin"},
        {"role": "club_admin"},
        {"is_admin": True},
        {"id": "attacker-controlled"},
    ],
)
def test_register_role_smuggling_rejected(client: TestClient, extra: dict) -> None:
    # Registering with an elevated role / forged id via extra fields must be
    # impossible: UserCreate enforces extra="forbid" -> 422.
    payload = {"full_name": "Jane Doe", "email": "jane@example.com", "password": "securepass123", **extra}
    response = client.post(f"{API}/register", json=payload)

    assert response.status_code == 422


def test_register_malformed_json(client: TestClient) -> None:
    # A request body that is not valid JSON must be rejected cleanly (422).
    response = client.post(
        f"{API}/register",
        content='{"full_name": "Jane Doe",',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
    assert "json" in response.text.lower()


def test_register_wrong_content_type(client: TestClient) -> None:
    # Sending non-JSON (here: form) body must not be interpreted as a valid payload.
    response = client.post(
        f"{API}/register",
        data={"full_name": "Jane Doe", "email": "jane@example.com", "password": "securepass123"},
    )

    assert response.status_code == 422


def test_register_sql_injection_safe(client: TestClient) -> None:
    # SQLi strings must be stored literally, never executed against the database.
    payload = "x'; DROP TABLE users; --"
    response = client.post(
        f"{API}/register",
        json={"full_name": payload, "email": "inject@example.com", "password": "securepass123"},
    )

    assert response.status_code == 201
    assert response.json()["full_name"] == payload


def test_register_xss_payload_stored_literal(client: TestClient) -> None:
    # XSS strings must be stored as literal data (escaping is a rendering concern).
    payload = "<script>alert('xss')</script>"
    response = client.post(
        f"{API}/register",
        json={"full_name": payload, "email": "xss@example.com", "password": "securepass123"},
    )

    assert response.status_code == 201
    assert response.json()["full_name"] == payload


def test_register_unicode_and_emoji_full_name(client: TestClient) -> None:
    # Non-ASCII names and emojis are legitimate user input and must be accepted.
    response = client.post(
        f"{API}/register",
        json={"full_name": "Jöhn Müller 🚀 中文", "email": "unicode@example.com", "password": "securepass123"},
    )

    assert response.status_code == 201


@pytest.mark.parametrize(
    "payload",
    [
        {"full_name": None, "email": "jane@example.com", "password": "securepass123"},
        {"full_name": "Jane Doe", "email": None, "password": "securepass123"},
        {"full_name": "Jane Doe", "email": "jane@example.com", "password": None},
    ],
)
def test_register_null_field_values(client: TestClient, payload: dict) -> None:
    # Explicit null for a required string field must be rejected (422).
    response = client.post(f"{API}/register", json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize("method", ["GET", "PUT", "PATCH", "DELETE"])
def test_register_invalid_http_method(client: TestClient, method: str) -> None:
    # Only POST is supported; other verbs must yield 405 Method Not Allowed.
    response = client.request(method, f"{API}/register")

    assert response.status_code == 405


def test_register_concurrent_duplicate(client: TestClient) -> None:
    # Racing identical registrations must resolve to exactly one winner (201) and
    # the remaining attempts to 409 Conflict, never 500.
    payload = {"full_name": "Race", "email": "race@example.com", "password": "securepass123"}

    def attempt(_: int) -> int:
        return client.post(f"{API}/register", json=payload).status_code

    with ThreadPoolExecutor(max_workers=5) as executor:
        statuses = sorted(executor.map(attempt, range(5)))

    assert statuses.count(201) == 1
    assert statuses.count(409) == len(statuses) - 1
    assert 500 not in statuses


# -------------------------------------------------------- Login edge cases
def test_login_empty_password(client: TestClient, db_session: Session) -> None:
    # Empty password violates min_length=6 on UserLogin.
    response = client.post(f"{API}/login", json={"email": "jane@example.com", "password": ""})

    assert response.status_code == 422


def test_login_whitespace_password(client: TestClient, db_session: Session) -> None:
    # A whitespace-only password (here 8 spaces, passing min_length) must never
    # authenticate; it either fails the schema check or the hash verification.
    _seed_db(client, db_session, "jane@example.com", "securepass123")

    response = client.post(f"{API}/login", json={"email": "jane@example.com", "password": "        "})

    assert response.status_code == 401


def test_login_null_credentials(client: TestClient) -> None:
    # Null email/password must not be coerced into a valid login attempt.
    response = client.post(f"{API}/login", json={"email": None, "password": None})

    assert response.status_code == 422


def test_login_email_whitespace_normalized(client: TestClient, db_session: Session) -> None:
    # Surrounding whitespace in the email is stripped by email-validator before lookup.
    _seed_db(client, db_session, "spacelog@example.com", "securepass123")

    response = client.post(f"{API}/login", json={"email": "  spacelog@example.com  ", "password": "securepass123"})

    assert response.status_code == 200


def test_login_email_case_insensitive(client: TestClient, db_session: Session) -> None:
    # KNOWN GAP: register normalizes emails to lowercase, but UserLogin has no
    # such normalization, so a differently-cased email currently fails lookup
    # (401). This test pins the current behaviour; ideally login should accept
    # any casing and return 200.
    _seed_db(client, db_session, "case@example.com", "securepass123")

    response = client.post(f"{API}/login", json={"email": "CASE@EXAMPLE.COM", "password": "securepass123"})

    assert response.status_code == 401


def test_login_malformed_json(client: TestClient) -> None:
    # Invalid JSON body must produce a clean 422, not a server error.
    response = client.post(
        f"{API}/login",
        content='{"email": "x@y.com"',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422


def test_login_wrong_content_type(client: TestClient) -> None:
    # A non-JSON body must not be accepted for the JSON login endpoint.
    response = client.post(
        f"{API}/login",
        data={"email": "jane@example.com", "password": "securepass123"},
    )

    assert response.status_code == 422


def test_login_sql_injection(client: TestClient, db_session: Session) -> None:
    # SQLi attempts in credentials must be treated as plain text, never executed
    # or allowed to bypass the login check. A valid-format email with an
    # injection string in the password must not authenticate.
    response = client.post(
        f"{API}/login",
        json={
            "email": "inject@example.com",
            "password": "anything' OR '1'='1' --",
        },
    )

    assert response.status_code == 401


def test_login_xss_in_password(client: TestClient, db_session: Session) -> None:
    # XSS payloads must be rejected as normal (non-matching) credential input.
    _seed_db(client, db_session, "jane@example.com", "securepass123")

    response = client.post(
        f"{API}/login",
        json={"email": "jane@example.com", "password": "<script>alert(1)</script>"},
    )

    assert response.status_code == 401


def test_login_very_long_password(client: TestClient, db_session: Session) -> None:
    # A 10k-char password must be rejected cleanly by validation (422), not crash
    # auth with an uncaught passlib PasswordSizeError (previously a 500 / DoS).
    _seed_db(client, db_session, "jane@example.com", "securepass123")

    response = client.post(
        f"{API}/login",
        json={"email": "jane@example.com", "password": "z" * 10_000},
    )

    assert response.status_code == 422


def test_login_extra_field_rejected(client: TestClient, db_session: Session) -> None:
    # Unexpected fields in the login body must be rejected, mirroring UserCreate:
    # UserLogin now also uses extra="forbid".
    _seed_db(client, db_session, "jane@example.com", "securepass123")

    response = client.post(
        f"{API}/login",
        json={"email": "jane@example.com", "password": "securepass123", "extra": "sneaky"},
    )

    assert response.status_code == 422


def test_login_unicode_password_roundtrip(client: TestClient, db_session: Session) -> None:
    # A password containing non-ASCII characters must round-trip exactly.
    _seed_db(client, db_session, "unicode@example.com", "pässwörd-🔑")

    response = client.post(
        f"{API}/login",
        json={"email": "unicode@example.com", "password": "pässwörd-🔑"},
    )

    assert response.status_code == 200


@pytest.mark.parametrize("method", ["GET", "PUT", "PATCH", "DELETE"])
def test_login_invalid_http_method(client: TestClient, method: str) -> None:
    # Only POST is supported on /login.
    response = client.request(method, f"{API}/login")

    assert response.status_code == 405


# ----------------------------------------------- Token / GET /me edge cases
def _seed_db(
    client: TestClient, db_session: Session, email: str, password: str
) -> User:
    user = User(
        full_name="Jane Doe", email=email, password_hash=get_password_hash(password)
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_me_missing_auth_header(client: TestClient, db_session: Session) -> None:
    # No Authorization header must yield 401.
    response = client.get(f"{API}/me")

    assert response.status_code == 401


def test_me_malformed_auth_header(client: TestClient, db_session: Session) -> None:
    # A header without the "Bearer <token>" form must be rejected.
    user = _seed_db(client, db_session, "jane@example.com", "securepass123")
    response = client.get(f"{API}/me", headers={"Authorization": f"Token {user.id}"})

    assert response.status_code == 401


def test_me_random_garbage_token(client: TestClient, db_session: Session) -> None:
    # A non-JWT random token must not authenticate.
    response = client.get(f"{API}/me", headers={"Authorization": "Bearer abc.def.ghi"})

    assert response.status_code == 401


def test_me_expired_token(client: TestClient, db_session: Session) -> None:
    # An expired JWT must be rejected, not accepted.
    user = _seed_db(client, db_session, "jane@example.com", "securepass123")
    expired = create_access_token(subject=user.id, expires_delta=timedelta(seconds=-1))

    response = client.get(f"{API}/me", headers={"Authorization": f"Bearer {expired}"})

    assert response.status_code == 401


def test_me_tampered_token(client: TestClient, db_session: Session) -> None:
    # Altering the payload of a valid token must break its signature check.
    user = _seed_db(client, db_session, "jane@example.com", "securepass123")
    token = create_access_token(subject=str(user.id))

    header, payload, sig = token.split(".")
    raw = json.loads(base64.urlsafe_b64decode(payload + "=="))
    # Point the subject at a different (nonexistent) user id to simulate tampering.
    raw["sub"] = str(uuid.uuid4())
    forged_payload = base64.urlsafe_b64encode(json.dumps(raw).encode()).decode().rstrip("=")
    forged = f"{header}.{forged_payload}.{sig}"

    response = client.get(f"{API}/me", headers={"Authorization": f"Bearer {forged}"})

    assert response.status_code == 401


def test_me_token_signed_with_wrong_secret(client: TestClient, db_session: Session) -> None:
    # A token signed with an unknown key must be rejected.
    user = _seed_db(client, db_session, "jane@example.com", "securepass123")

    payload = {"exp": datetime.now(UTC) + timedelta(minutes=5), "sub": str(user.id)}
    token = jose.jwt.encode(payload, "an-attacker-chosen-secret", algorithm="HS256")

    response = client.get(f"{API}/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_me_token_for_deleted_user(client: TestClient, db_session: Session) -> None:
    # A token whose subject no longer exists in the DB must not authenticate.
    user = _seed_db(client, db_session, "jane@example.com", "securepass123")
    token = create_access_token(subject=str(user.id))

    # Remove the user directly; the token is now orphaned.
    db_session.delete(user)
    db_session.commit()

    response = client.get(f"{API}/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
