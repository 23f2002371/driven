"""Token schemas for the authentication flow."""

from __future__ import annotations

from pydantic import BaseModel


class Token(BaseModel):
    """Access token returned after a successful login."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Decoded JWT payload (used internally)."""

    sub: str | None = None
