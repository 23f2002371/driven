"""Student model.

Stores profile information for a single student. Authentication data lives on
the related :class:`~app.models.user.User` model.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.utils.enums import Department

if TYPE_CHECKING:
    from app.models.bounty import Application
    from app.models.domain import StudentDomain
    from app.models.event import Certificate, EventRegistration
    from app.models.inventory import (
        BorrowDetail,  #has to push Anshul-----------------------------------------------------
    )
    from app.models.user import User


class Student(Base):

    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    student_id: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
    )
    department: Mapped[Department] = mapped_column(
        Enum(
            Department,
            name="department",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )

    phone: Mapped[str | None] = mapped_column(String(20))
    github_url: Mapped[str | None] = mapped_column(String(100))
    linkedin_url: Mapped[str | None] = mapped_column(String(100))
    portfolio_url: Mapped[str | None] = mapped_column(String(255))

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

    user: Mapped[User] = relationship(
        "User",
        back_populates="student",
    )
    registrations: Mapped[list[EventRegistration]] = relationship(
        "EventRegistration",
        back_populates="student",
    )
    domains: Mapped[list[StudentDomain]] = relationship(
        "StudentDomain",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    certificates: Mapped[list[Certificate]] = relationship(
        "Certificate",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    borrow_details: Mapped[list[BorrowDetail]] = relationship(
        "BorrowDetail",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    bounties_applications: Mapped[list[Application]] = relationship(
        "Application",
        back_populates="student",
        cascade="all, delete-orphan",
    )


    def __repr__(self) -> str:
        return f"<Student id={self.id}>"