"""Pydantic schemas for the Campus Bounties domain."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.utils.enums import (
    ApplicationStatus,
    BountyStatus,
    DeliverableStatus,
    Department,
    DomainEnum,
    TechnologyEnum,
    WorkStatus,
)


# ---------------------------------------------------------------- Bounty
class DomainInfo(BaseModel):
    """Domain referenced by a bounty."""

    id: UUID
    name: DomainEnum


class TechnologyItem(BaseModel):
    """A technology required by a bounty."""

    id: UUID
    name: TechnologyEnum


class ResponsibilityItem(BaseModel):
    """A single responsibility of a bounty."""

    id: UUID
    title: str


class BountyCreate(BaseModel):
    """Payload to create a bounty (club admin only).

    ``created_by`` and ``status`` are intentionally absent: the creator is
    derived from the authenticated admin and new bounties start as ``open``.
    """

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    domain_id: UUID
    description: str = Field(min_length=1)
    reward: Decimal = Field(ge=0)
    application_deadline: datetime
    duration: str = Field(min_length=1, max_length=50)
    student_seats: int = Field(ge=1)
    image_url: str | None = None
    technologies: list[UUID] = []
    responsibilities: list[str] = []


class BountyUpdate(BaseModel):
    """Payload to update a bounty (club admin only).

    Protected fields (``id``, ``created_by``, ``status``) are not part of this
    schema, so they are rejected with 422 via ``extra="forbid"``.
    """

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    domain_id: UUID | None = None
    description: str | None = Field(default=None, min_length=1)
    reward: Decimal | None = Field(default=None, ge=0)
    application_deadline: datetime | None = None
    duration: str | None = Field(default=None, min_length=1, max_length=50)
    student_seats: int | None = Field(default=None, ge=1)
    image_url: str | None = None
    technologies: list[UUID] | None = None
    responsibilities: list[str] | None = None


class BountyResponse(BaseModel):
    """Full representation of a bounty with its related entities."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    domain: DomainInfo
    description: str
    reward: Decimal
    application_deadline: datetime
    duration: str
    student_seats: int
    image_url: str | None
    status: BountyStatus
    technologies: list[TechnologyItem] = []
    responsibilities: list[ResponsibilityItem] = []
    created_by: UUID
    created_by_name: str | None
    created_at: datetime
    updated_at: datetime


# ----------------------------------------------------------- Application
class ApplicationCreate(BaseModel):
    """Payload for a student to apply to a bounty.

    ``student_id`` and ``status`` are intentionally absent; they are derived
    from the authenticated student and always start as ``pending``.
    """

    model_config = ConfigDict(extra="forbid")

    availability: str = Field(min_length=1, max_length=50)
    resume: str | None = None


class ApplicationUpdate(BaseModel):
    """Payload to update an application (club admin only).

    Only ``status`` is editable; all other fields are rejected via
    ``extra="forbid"``.
    """

    model_config = ConfigDict(extra="forbid")

    status: ApplicationStatus


class StudentInfo(BaseModel):
    """Student information embedded in an application response."""

    id: UUID
    name: str
    email: str
    student_id: str
    department: Department


class ApplicationResponse(BaseModel):
    """Representation of an application with its bounty and student info."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    bounty_id: UUID
    student_id: UUID
    availability: str
    resume: str | None
    status: ApplicationStatus
    created_at: datetime
    updated_at: datetime
    bounty: BountyResponse
    student: StudentInfo
    matched_technologies: list[TechnologyEnum] = []


# ---------------------------------------------------------------- Work
class DeliverableCreateItem(BaseModel):
    """A deliverable submitted when assigning work."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)


class WorkCreate(BaseModel):
    """Payload to assign work to an accepted application (club admin only)."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    task_description: str = Field(min_length=1)
    deadline: datetime
    event_id: UUID | None = None
    deliverables: list[DeliverableCreateItem] = []


class DeliverableStatusItem(BaseModel):
    """A deliverable status update keyed by its id."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    status: DeliverableStatus


class WorkUpdateByStudent(BaseModel):
    """Payload for a student to update their assigned work.

    Only progress fields (``status`` and deliverable statuses) are allowed;
    anything else is rejected with 422 via ``extra="forbid"``.
    """

    model_config = ConfigDict(extra="forbid")

    status: WorkStatus | None = None
    deliverables: list[DeliverableStatusItem] | None = None


class WorkUpdateByAdmin(BaseModel):
    """Payload for the club admin to update work.

    ``application_id`` is intentionally absent so the work stays tied to its
    accepted application.
    """

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    task_description: str | None = Field(default=None, min_length=1)
    deadline: datetime | None = None
    event_id: UUID | None = None
    status: WorkStatus | None = None
    deliverables: list[DeliverableStatusItem] | None = None


class DeliverableResponse(BaseModel):
    """Representation of a single deliverable."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    work_id: UUID
    title: str
    status: DeliverableStatus


class EventInfo(BaseModel):
    """Event linked to a work record."""

    id: UUID
    name: str


class ApplicationSummary(BaseModel):
    """Lightweight application info embedded in a work response."""

    id: UUID
    bounty_id: UUID
    student_id: UUID
    status: ApplicationStatus
    bounty_title: str
    student_name: str


class WorkResponse(BaseModel):
    """Full representation of assigned work."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    application_id: UUID
    title: str
    task_description: str
    deadline: datetime
    event_id: UUID | None
    status: WorkStatus
    created_at: datetime
    updated_at: datetime
    deliverables: list[DeliverableResponse] = []
    event: EventInfo | None = None
    application: ApplicationSummary | None = None