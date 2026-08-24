"""Event models.

Top-level representation of an event (``Event``) plus its supporting detail
models (``EventAgenda``, ``AdditionalEventInfo``, ``EventMentor``), all in a
single module.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, time
from typing import TYPE_CHECKING


from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.utils.enums import (
    AdditionalInfoType,
    AttendanceStatus,
    CertificateType,
    EventCategory,
    EventRejectionReason,
    EventStatus,
    EventVenue,
    RegistrationStatus,
    WinnerPosition,
)


if TYPE_CHECKING:
    from app.models.bounty import Work
    from app.models.student import Student
    from backend.app.models.support_desk import DiscussionThread



class Event(Base):

    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    short_description: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[EventCategory] = mapped_column(
        Enum(
            EventCategory,
            name="event_category",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    registration_deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    venue: Mapped[EventVenue] = mapped_column(
        Enum(
            EventVenue,
            name="event_venue",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    max_participants: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[EventStatus] = mapped_column(
        Enum(
            EventStatus,
            name="event_status",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        default=EventStatus.PENDING,
        server_default=EventStatus.PENDING.value,
        nullable=False,
    )
    cover_image_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    agendas: Mapped[list[EventAgenda]] = relationship(
        "EventAgenda",
        back_populates="event",
        cascade="all, delete-orphan",
    )
    additional_info: Mapped[list[AdditionalEventInfo]] = relationship(
        "AdditionalEventInfo",
        back_populates="event",
        cascade="all, delete-orphan",
    )
    mentors: Mapped[list[EventMentor]] = relationship(
        "EventMentor",
        back_populates="event",
        cascade="all, delete-orphan",
    )
    registrations: Mapped[list[EventRegistration]] = relationship(
        "EventRegistration",
        back_populates="event",
        cascade="all, delete-orphan",
    )
    winners: Mapped[list[EventWinner]] = relationship(
        "EventWinner",
        back_populates="event",
        cascade="all, delete-orphan",
    )
    certificates: Mapped[list[Certificate]] = relationship(
        "Certificate",
        back_populates="event",
        cascade="all, delete-orphan",
    )
    discussion_thread: Mapped[DiscussionThread | None] = relationship(
        "DiscussionThread",
        back_populates="event",
        cascade="all, delete-orphan",
        uselist=False,
    )
    rejection_reason: Mapped[EventRejectReason | None] = relationship(
        "EventRejectReason",
        back_populates="event",
        cascade="all, delete-orphan",
        uselist=False,
    )
    works: Mapped[list[Work]] = relationship(
        "Work",
        back_populates="event",
    )


    def __repr__(self) -> str:
        return f"<Event id={self.id} name={self.name!r} status={self.status}>"


class EventAgenda(Base):
    """One time-boxed entry on an event's agenda."""

    __tablename__ = "event_agenda_schedule"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    start_time: Mapped[time | None] = mapped_column(Time(timezone=False))
    end_time: Mapped[time | None] = mapped_column(Time(timezone=False))
    title: Mapped[str | None] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(Text)

    event: Mapped[Event] = relationship("Event", back_populates="agendas")

    def __repr__(self) -> str:
        return f"<EventAgenda id={self.id} title={self.title!r}>"


class AdditionalEventInfo(Base):
    """One additional info section for an event."""

    __tablename__ = "additional_event_info"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    section_type: Mapped[AdditionalInfoType] = mapped_column(
        Enum(
            AdditionalInfoType,
            name="additional_info_type",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    content: Mapped[str | None] = mapped_column(Text)

    event: Mapped[Event] = relationship("Event", back_populates="additional_info")

    def __repr__(self) -> str:
        return f"<AdditionalEventInfo id={self.id} section_type={self.section_type}>"


class EventMentor(Base):
    """One mentor attached to an event."""

    __tablename__ = "event_mentors"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str | None] = mapped_column(String(100))
    company: Mapped[str | None] = mapped_column(String(150))
    designation: Mapped[str | None] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(150))
    linkedin_url: Mapped[str | None] = mapped_column(Text)

    event: Mapped[Event] = relationship("Event", back_populates="mentors")

    def __repr__(self) -> str:
        return f"<EventMentor id={self.id} name={self.name!r}>"


class EventRegistration(Base):
    """A student's registration for an event."""

    __tablename__ = "event_registrations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    team_name: Mapped[str] = mapped_column(String(150), nullable=False)
    qr_code_url: Mapped[str | None] = mapped_column(Text)
    registration_status: Mapped[RegistrationStatus] = mapped_column(
        Enum(
            RegistrationStatus,
            name="registration_status",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        default=RegistrationStatus.PENDING,
        server_default=RegistrationStatus.PENDING.value,
        nullable=False,
    )
    attendance_status: Mapped[AttendanceStatus] = mapped_column(
        Enum(
            AttendanceStatus,
            name="attendance_status",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        default=AttendanceStatus.ABSENT,
        server_default=AttendanceStatus.ABSENT.value,
        nullable=False,
    )

    event: Mapped[Event] = relationship("Event", back_populates="registrations")
    student: Mapped[Student] = relationship("Student", back_populates="registrations")
    winner: Mapped[EventWinner | None] = relationship(
        "EventWinner",
        back_populates="registration",
        uselist=False,
    )
    certificate: Mapped[Certificate | None] = relationship(
        "Certificate",
        back_populates="registration",
        uselist=False,
    )

    def __repr__(self) -> str:
        return (
            f"<EventRegistration id={self.id} "
            f"event_id={self.event_id} student_id={self.student_id}>"
        )


class EventWinner(Base):

    __tablename__ = "event_winners"
    __table_args__ = (
        UniqueConstraint(
            "event_id",
            "position",
            name="uq_event_winners_event_position",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    registration_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("event_registrations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    position: Mapped[WinnerPosition] = mapped_column(
        Enum(
            WinnerPosition,
            name="winner_position",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    project_name: Mapped[str] = mapped_column(String(200), nullable=False)
    project_url: Mapped[str | None] = mapped_column(Text)

    event: Mapped[Event] = relationship("Event", back_populates="winners")
    registration: Mapped[EventRegistration] = relationship(
        "EventRegistration",
        back_populates="winner",
    )

    def __repr__(self) -> str:
        return (
            f"<EventWinner id={self.id} event_id={self.event_id} "
            f"position={self.position}>"
        )


class Certificate(Base):
    """A certificate issued for an event registration."""

    __tablename__ = "certificates"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    registration_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("event_registrations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    certificate_type: Mapped[CertificateType] = mapped_column(
        Enum(
            CertificateType,
            name="certificate_type",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    certificate_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    event: Mapped[Event] = relationship("Event", back_populates="certificates")
    student: Mapped[Student] = relationship("Student", back_populates="certificates")
    registration: Mapped[EventRegistration] = relationship(
        "EventRegistration",
        back_populates="certificate",
    )

    def __repr__(self) -> str:
        return (
            f"<Certificate id={self.id} event_id={self.event_id} "
            f"certificate_type={self.certificate_type}>"
        )


class EventRejectReason(Base):
    """Reason and optional alternatives provided when an event request is rejected."""

    __tablename__ = "event_reject_reasons"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    reason: Mapped[EventRejectionReason] = mapped_column(
        Enum(
            EventRejectionReason,
            name="event_rejection_reason",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    alternative_venue: Mapped[EventVenue | None] = mapped_column(
        Enum(
            EventVenue,
            name="event_venue",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=True,
    )
    alternative_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    admin_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    event: Mapped[Event] = relationship("Event", back_populates="rejection_reason")

    def __repr__(self) -> str:
        return f"<EventRejectReason id={self.id} event_id={self.event_id} reason={self.reason}>"