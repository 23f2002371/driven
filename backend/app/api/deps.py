"""Shared FastAPI dependencies for authentication and authorization.

- ``get_current_user`` extracts the JWT from the Authorization header and
  resolves it to a :class:`~app.models.user.User`.
- ``require_roles`` guards an endpoint so only users with one of the given
  roles may access it.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.utils.enums import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_STR}/auth/login")

# Reusable dependency aliases.
DbSession = Annotated[Session, Depends(get_db)]

_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DbSession,
) -> User:
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise _CREDENTIALS_EXCEPTION from None

    user_id = payload.get("sub")
    if user_id is None:
        raise _CREDENTIALS_EXCEPTION

    try:
        parsed_id = uuid.UUID(user_id)
    except (ValueError, TypeError):
        raise _CREDENTIALS_EXCEPTION from None

    user = db.get(User, parsed_id)
    if user is None:
        raise _CREDENTIALS_EXCEPTION
    return user


def require_roles(*roles: UserRole) -> Callable[[User], User]:

    def _checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _checker


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))
