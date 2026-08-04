"""Pydantic schemas package."""

from app.schemas.event import (
    EventCreate,
    EventRegistrationCreate,
    EventRegistrationResponse,
    EventRegistrationUpdate,
    EventResponse,
    EventUpdate,
    EventWinnerCreate,
    EventWinnerResponse,
    EventWinnerUpdate,
    PrivateEventResponse,
)
from app.schemas.student import (
    StudentCreate,
    StudentResponse,
    StudentSkillCreate,
    StudentSkillResponse,
    StudentSkillUpdate,
    StudentUpdate,
)
from app.schemas.token import Token, TokenPayload
from app.schemas.user import UserCreate, UserLogin, UserResponse

__all__ = [
    "EventCreate",
    "EventRegistrationCreate",
    "EventRegistrationResponse",
    "EventRegistrationUpdate",
    "EventResponse",
    "EventUpdate",
    "EventWinnerCreate",
    "EventWinnerResponse",
    "EventWinnerUpdate",
    "PrivateEventResponse",
    "StudentCreate",
    "StudentResponse",
    "StudentSkillCreate",
    "StudentSkillResponse",
    "StudentSkillUpdate",
    "StudentUpdate",
    "Token",
    "TokenPayload",
    "UserCreate",
    "UserLogin",
    "UserResponse",
]