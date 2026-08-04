"""Pydantic schemas for the Event domain."""

from __future__ import annotations

from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.utils.enums import (
    AdditionalInfoType,
    AttendanceStatus,
    EventCategory,
    EventStatus,
    EventVenue,
    RegistrationStatus,
    WinnerPosition,
)


# ------------------------------------------------- Nested child items
class AgendaItem(BaseModel):
    """A single time-boxed agenda entry embedded in an event payload."""

    model_config = ConfigDict(from_attributes=True)

    start_time: time | None = None
    end_time: time | None = None
    title: str | None = Field(default=None, max_length=150)
    description: str | None = None


class AdditionalInfoItem(BaseModel):
    """A single additional info section embedded in an event payload."""

    model_config = ConfigDict(from_attributes=True)

    section_type: AdditionalInfoType
    content: str | None = None


class MentorItem(BaseModel):
    """A single mentor embedded in an event payload."""

    model_config = ConfigDict(from_attributes=True)

    name: str | None = Field(default=None, max_length=100)
    company: str | None = Field(default=None, max_length=150)
    designation: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None
    linkedin_url: str | None = None


# ---------------------------------------------------------------- Event
class EventCreate(BaseModel):
    """Payload to create an event.

    The frontend submits the complete event - basic details plus its child
    entities (agenda, additional info, and mentors) - in a single request.
    ``status`` is intentionally absent: new events always start as ``pending``
    and can only be approved/rejected by an admin.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=150)
    short_description: str = Field(min_length=1, max_length=255)
    category: EventCategory
    event_date: date
    registration_deadline: datetime
    venue: EventVenue
    max_participants: int = Field(ge=1)
    description: str = Field(min_length=1)
    cover_image_url: str | None = None

    agendas: list[AgendaItem] = []
    additional_info: list[AdditionalInfoItem] = []
    mentors: list[MentorItem] = []


class EventUpdate(BaseModel):
    """Payload to update an event. Every field is optional."""

    name: str | None = Field(default=None, min_length=1, max_length=150)
    short_description: str | None = Field(default=None, min_length=1, max_length=255)
    category: EventCategory | None = None
    event_date: date | None = None
    registration_deadline: datetime | None = None
    venue: EventVenue | None = None
    max_participants: int | None = Field(default=None, ge=1)
    description: str | None = Field(default=None, min_length=1)
    status: EventStatus | None = None
    cover_image_url: str | None = None

    agendas: list[AgendaItem] | None = None
    additional_info: list[AdditionalInfoItem] | None = None
    mentors: list[MentorItem] | None = None


class EventResponse(BaseModel):
    """Public representation of an event."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    short_description: str
    category: EventCategory
    event_date: date
    venue: EventVenue
    max_participants: int
    description: str
    cover_image_url: str | None
    winner_name: str | None
    winner_project_url: str | None


class PrivateEventResponse(BaseModel):
    """Full representation of an event including its child entities."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    short_description: str
    category: EventCategory
    event_date: date
    registration_deadline: datetime
    venue: EventVenue
    max_participants: int
    description: str
    status: EventStatus
    cover_image_url: str | None
    created_at: datetime
    updated_at: datetime

    agendas: list[AgendaItem] = []
    additional_info: list[AdditionalInfoItem] = []
    mentors: list[MentorItem] = []


# ---------------------------------------------------------- Registration
class EventRegistrationCreate(BaseModel):
    """Payload to register a student for an event."""

    model_config = ConfigDict(extra="forbid")

    event_id: UUID
    student_id: UUID
    team_name: str = Field(min_length=1, max_length=150)
    qr_code_url: str | None = None


class EventRegistrationUpdate(BaseModel):
    """Payload to update a registration. Every field is optional."""

    team_name: str | None = Field(default=None, min_length=1, max_length=150)
    qr_code_url: str | None = None
    registration_status: RegistrationStatus | None = None
    attendance_status: AttendanceStatus | None = None


class EventRegistrationResponse(BaseModel):
    """Public representation of an event registration."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event_id: UUID
    student_id: UUID
    team_name: str
    qr_code_url: str | None
    registration_status: RegistrationStatus
    attendance_status: AttendanceStatus


# -------------------------------------------------------------- Winner
class EventWinnerCreate(BaseModel):
    """Payload to create an event winner."""

    model_config = ConfigDict(extra="forbid")

    event_id: UUID
    registration_id: UUID
    position: WinnerPosition
    project_name: str = Field(min_length=1, max_length=200)


class EventWinnerUpdate(BaseModel):
    """Payload to update an event winner. Every field is optional."""

    position: WinnerPosition | None = None
    project_name: str | None = Field(default=None, min_length=1, max_length=200)


class EventWinnerResponse(BaseModel):
    """Public representation of an event winner."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event_id: UUID
    registration_id: UUID
    position: WinnerPosition
    project_name: str