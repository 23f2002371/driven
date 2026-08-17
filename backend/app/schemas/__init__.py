"""Pydantic schemas package."""

from app.schemas.bounty import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
    BountyCreate,
    BountyResponse,
    BountyUpdate,
    WorkCreate,
    WorkResponse,
    WorkUpdateByAdmin,
    WorkUpdateByStudent,
)
from app.schemas.event import (
    CertificateResponse,
    EventCreate,
    EventRegistrationCreate,
    EventRegistrationResponse,
    EventRegistrationUpdate,
    EventResponse,
    EventUpdate,
    EventWinnerCreate,
    EventWinnerResponse,
    PrivateEventResponse,
)
from app.schemas.student import (
    DomainItem,
    StudentCreate,
    StudentResponse,
    StudentUpdate,
    TechnologyItem,
)
from app.schemas.token import Token, TokenPayload
from app.schemas.user import UserCreate, UserLogin, UserResponse

__all__ = [
    "AdditionalEventInfo",
    "ApplicationCreate",
    "ApplicationResponse",
    "ApplicationUpdate",
    "BountyCreate",
    "BountyResponse",
    "BountyUpdate",
    "CertificateResponse",
    "DomainItem",
    "EventCreate",
    "EventRegistrationCreate",
    "EventRegistrationResponse",
    "EventRegistrationUpdate",
    "EventResponse",
    "EventUpdate",
    "EventWinnerCreate",
    "EventWinnerResponse",
    "PrivateEventResponse",
    "StudentCreate",
    "StudentResponse",
    "StudentUpdate",
    "TechnologyItem",
    "Token",
    "TokenPayload",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "WorkCreate",
    "WorkResponse",
    "WorkUpdateByAdmin",
    "WorkUpdateByStudent",
]