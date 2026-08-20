"""Authentication endpoints.

- ``POST /auth/register``            - create a student account.
- ``POST /auth/login``               - exchange credentials for an access token.
- ``GET  /auth/me``                  - return the authenticated user's profile.
- ``GET  /auth/google/login``        - redirect to Google's OAuth consent screen.
- ``GET  /auth/google/callback``     - handle Google's OAuth callback.
- ``GET  /auth/github/login``        - redirect to GitHub's OAuth consent screen.
- ``GET  /auth/github/callback``     - handle GitHub's OAuth callback.
"""

from __future__ import annotations

from typing import Annotated

from authlib.integrations.base_client import OAuthError
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from starlette.responses import RedirectResponse

from app.api.deps import DbSession, get_current_user, get_user_by_email
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.utils.enums import UserRole

router = APIRouter()

CurrentUser = Annotated[User, Depends(get_current_user)]

# OAuth 2.0 registry (Authlib) for social login.
oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)
oauth.register(
    name="github",
    client_id=settings.GITHUB_CLIENT_ID,
    client_secret=settings.GITHUB_CLIENT_SECRET,
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)


def _oauth_login_or_create(
    db: DbSession,
    *,
    email: str,
    full_name: str,
) -> RedirectResponse:
    
    user = get_user_by_email(db, email)

    if user is None:
        user = User(full_name=full_name, email=email, role=UserRole.STUDENT)
        db.add(user)
        try:
            db.commit()
        except IntegrityError:
            # Concurrent first login with the same email.
            db.rollback()
            user = get_user_by_email(db, email)
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user",
                ) from None
        else:
            db.refresh(user)

   
    try:
        access_token = create_access_token(subject=user.id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate token",
        ) from exc

    
    return RedirectResponse(
        url=f"{settings.FRONTEND_URL}/auth/oauth-success?token={access_token}"
    )

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: DbSession) -> User:
    
    if get_user_by_email(db, payload.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        role=UserRole.STUDENT,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # Race condition: another request created the same email meanwhile.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        ) from None
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: DbSession) -> Token:
    
    user = get_user_by_email(db, payload.email)

    # OAuth-only users have no password_hash; password login is invalid for them.
    if (
        user is None
        or user.password_hash is None
        or not verify_password(payload.password, user.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(subject=user.id))


@router.get("/me", response_model=UserResponse)
def read_me(current_user: CurrentUser) -> User:
    
    return current_user


@router.get("/google/login")
async def google_login(request: Request) -> RedirectResponse:
    """OAuth redirect: send the user to Google's consent screen."""
    # Build the callback URL from the incoming request so it always points at
    # the same host that started the flow (OAuth `state` lives in a cookie on
    # that host). Using settings.BACKEND_URL here breaks when it is unset or
    # differs from the host users actually reach.
    redirect_uri = str(request.url_for("google_callback"))
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: DbSession) -> RedirectResponse:
    """Callback processing: verify the OAuth token, read the profile, then log
    the user in (creating the account on first login)."""
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Google authorization",
        ) from None

    # Read the profile returned by Google's userinfo endpoint.
    userinfo = await oauth.google.userinfo(token=token)
    email = userinfo.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account has no email address",
        )

    full_name = userinfo.get("name") or email
    return _oauth_login_or_create(db, email=email, full_name=full_name)


@router.get("/github/login")
async def github_login(request: Request) -> RedirectResponse:
    """OAuth redirect: send the user to GitHub's consent screen."""
    # Same rationale as google_login: derive the callback from the request host.
    redirect_uri = str(request.url_for("github_callback"))
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/github/callback")
async def github_callback(request: Request, db: DbSession) -> RedirectResponse:
    """Callback processing: verify the OAuth token, read the profile, then log
    the user in (creating the account on first login)."""
    try:
        token = await oauth.github.authorize_access_token(request)
    except OAuthError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired GitHub authorization",
        ) from None

    # Read the GitHub profile.
    profile = (await oauth.github.get("user", token=token)).json()
    email = profile.get("email")

    # GitHub hides the email by default; fetch the primary verified one.
    if not email:
        emails = (await oauth.github.get("user/emails", token=token)).json()
        for entry in emails:
            if entry.get("primary") and entry.get("verified"):
                email = entry.get("email")
                break

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub account has no verified email",
        )

    full_name = profile.get("name") or profile.get("login") or email
    return _oauth_login_or_create(db, email=email, full_name=full_name)
