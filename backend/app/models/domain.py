"""Student skill domain models.

Normalized hierarchy for a student's declared skills:

    Domain (1) ----> (N) Technology
    ----> Student (1) ----> (N) StudentDomain (1) ----> (N) StudentTechnology

A student picks one or several domains; for every selected domain they can name
any number of technologies that fall under it.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Uuid, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.utils.enums import DomainEnum, TechnologyEnum

if TYPE_CHECKING:
    from app.models.student import Student


class Domain(Base):

    __tablename__ = "domains"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[DomainEnum] = mapped_column(
        Enum(
            DomainEnum,
            name="domain_enum",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        unique=True,
    )

    technologies: Mapped[list[Technology]] = relationship(
        "Technology",
        back_populates="domain",
        cascade="all, delete-orphan",
    )
    student_domains: Mapped[list[StudentDomain]] = relationship(
        "StudentDomain",
        back_populates="domain",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Domain id={self.id} name={self.name!r}>"


class Technology(Base):

    __tablename__ = "technologies"
    __table_args__ = (
        UniqueConstraint(
            "domain_id",
            "name",
            name="uq_technologies_domain_name",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    domain_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("domains.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[TechnologyEnum] = mapped_column(
        Enum(
            TechnologyEnum,
            name="technology_enum",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )

    domain: Mapped[Domain] = relationship("Domain", back_populates="technologies")
    student_technologies: Mapped[list[StudentTechnology]] = relationship(
        "StudentTechnology",
        back_populates="technology",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Technology id={self.id} name={self.name!r}>"


class StudentDomain(Base):
    """A domain selected by a student."""

    __tablename__ = "student_domains"
    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "domain_id",
            name="uq_student_domains_student_domain",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    domain_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("domains.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    student: Mapped[Student] = relationship("Student", back_populates="domains")
    domain: Mapped[Domain] = relationship("Domain", back_populates="student_domains")
    technologies: Mapped[list[StudentTechnology]] = relationship(
        "StudentTechnology",
        back_populates="student_domain",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<StudentDomain id={self.id} student_id={self.student_id} "
            f"domain_id={self.domain_id}>"
        )


class StudentTechnology(Base):
    """A technology a student selected within one of their domains."""

    __tablename__ = "student_technologies"
    __table_args__ = (
        UniqueConstraint(
            "student_domain_id",
            "technology_id",
            name="uq_student_technologies_student_domain_technology",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    student_domain_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("student_domains.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    technology_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("technologies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    student_domain: Mapped[StudentDomain] = relationship(
        "StudentDomain",
        back_populates="technologies",
    )
    technology: Mapped[Technology] = relationship(
        "Technology",
        back_populates="student_technologies",
    )

    def __repr__(self) -> str:
        return (
            f"<StudentTechnology id={self.id} "
            f"student_domain_id={self.student_domain_id} "
            f"technology_id={self.technology_id}>"
        )