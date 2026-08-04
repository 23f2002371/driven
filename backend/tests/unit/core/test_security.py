"""Unit tests for :mod:`app.core.security`.

These tests run against the security helpers directly without any HTTP or
database involvement.
"""

from __future__ import annotations

import uuid

from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


def test_get_password_hash_differs_from_plaintext() -> None:
    hashed = get_password_hash("supersecret")

    assert hashed != "supersecret"
    assert hashed.startswith(("$2", "$2a", "$2b"))


def test_verify_password_correct() -> None:
    hashed = get_password_hash("supersecret")

    assert verify_password("supersecret", hashed) is True


def test_verify_password_wrong() -> None:
    hashed = get_password_hash("supersecret")

    assert verify_password("wrongpass", hashed) is False


def test_create_access_token_returns_jwt() -> None:
    token = create_access_token(subject="user-123")

    assert isinstance(token, str)
    assert token.count(".") == 2


def test_decode_access_token_returns_original_subject() -> None:
    subject = str(uuid.uuid4())
    token = create_access_token(subject=subject)

    payload = decode_access_token(token)

    assert payload["sub"] == subject
