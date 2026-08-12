"""Campus Bounties model layer.

A :class:`Bounty` is an opportunity created by the club admin. Students apply
through :class:`Application`; accepted applicants are handed a :class:`Work`
record against which they produce :class:`Deliverable` items.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.utils.enums import (
    ApplicationStatus,
    BountyStatus,
    DeliverableStatus,
    WorkStatus,
)

if TYPE_CHECKING:
    from app.models.domain import Domain, Technology
    from app.models.event import Event
    from app.models.student import Student
    from app.models.user import User


class Bounty(Base):
    """An opportunity created by the club admin."""

    __tablename__ = "bounties"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    domain_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("domains.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    reward: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    application_deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    duration: Mapped[str] = mapped_column(String(50), nullable=False)
    student_seats: Mapped[int] = mapped_column(Integer, nullable=False)
    image_url: Mapped[str | None] = mapped_column(Text)
    status: Mapped[BountyStatus] = mapped_column(
        Enum(
            BountyStatus,
            name="bounty_status",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        default=BountyStatus.OPEN,
        server_default=BountyStatus.OPEN.value,
        nullable=False,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
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

    domain: Mapped[Domain] = relationship("Domain", back_populates="bounties")
    created_by_user: Mapped[User] = relationship(
        "User",
        back_populates="bounties_created",
    )
    technologies: Mapped[list[BountyTechnology]] = relationship(
        "BountyTechnology",
        back_populates="bounty",
        cascade="all, delete-orphan",
    )
    responsibilities: Mapped[list[Responsibility]] = relationship(
        "Responsibility",
        back_populates="bounty",
        cascade="all, delete-orphan",
    )
    applications: Mapped[list[Application]] = relationship(
        "Application",
        back_populates="bounty",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Bounty id={self.id} title={self.title!r} status={self.status}>"


class BountyTechnology(Base):
    """A technology required by a bounty."""

    __tablename__ = "bounty_technologies"
    __table_args__ = (
        UniqueConstraint(
            "bounty_id",
            "technology_id",
            name="uq_bounty_technologies_bounty_technology",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    bounty_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("bounties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    technology_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("technologies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    bounty: Mapped[Bounty] = relationship("Bounty", back_populates="technologies")
    technology: Mapped[Technology] = relationship(
        "Technology",
        back_populates="bounties",
    )

    def __repr__(self) -> str:
        return (
            f"<BountyTechnology id={self.id} bounty_id={self.bounty_id} "
            f"technology_id={self.technology_id}>"
        )


class Responsibility(Base):
    """One responsibility tied to a bounty."""

    __tablename__ = "responsibilities"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    bounty_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("bounties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)

    bounty: Mapped[Bounty] = relationship("Bounty", back_populates="responsibilities")

    def __repr__(self) -> str:
        return f"<Responsibility id={self.id} title={self.title!r}>"


class Application(Base):
    """A student's application to a bounty."""

    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint(
            "bounty_id",
            "student_id",
            name="uq_applications_bounty_student",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    bounty_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("bounties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    availability: Mapped[str] = mapped_column(String(50), nullable=False)
    # Stores the uploaded resume's reference/path, never the PDF binary itself.
    resume: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(
            ApplicationStatus,
            name="application_status",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        default=ApplicationStatus.PENDING,
        server_default=ApplicationStatus.PENDING.value,
        nullable=False,
    )
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

    bounty: Mapped[Bounty] = relationship("Bounty", back_populates="applications")
    student: Mapped[Student] = relationship(
        "Student",
        back_populates="bounties_applications",
    )
    work: Mapped[Work | None] = relationship(
        "Work",
        back_populates="application",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Application id={self.id} bounty_id={self.bounty_id} "
            f"student_id={self.student_id} status={self.status}>"
        )


class Work(Base):
    """Work assigned to a student once their application is accepted."""

    __tablename__ = "works"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    task_description: Mapped[str] = mapped_column(Text, nullable=False)
    deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    event_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("events.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[WorkStatus] = mapped_column(
        Enum(
            WorkStatus,
            name="work_status",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        default=WorkStatus.ASSIGNED,
        server_default=WorkStatus.ASSIGNED.value,
        nullable=False,
    )
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

    application: Mapped[Application] = relationship(
        "Application",
        back_populates="work",
    )
    event: Mapped[Event | None] = relationship("Event", back_populates="works")
    deliverables: Mapped[list[Deliverable]] = relationship(
        "Deliverable",
        back_populates="work",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Work id={self.id} application_id={self.application_id} "
            f"title={self.title!r} status={self.status}>"
        )


class Deliverable(Base):
    """A single deliverable a student must produce for their work."""

    __tablename__ = "deliverables"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    work_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("works.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[DeliverableStatus] = mapped_column(
        Enum(
            DeliverableStatus,
            name="deliverable_status",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        default=DeliverableStatus.PENDING,
        server_default=DeliverableStatus.PENDING.value,
        nullable=False,
    )

    work: Mapped[Work] = relationship("Work", back_populates="deliverables")

    def __repr__(self) -> str:
        return f"<Deliverable id={self.id} title={self.title!r} status={self.status}>"