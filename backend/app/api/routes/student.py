"""Student profile routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import DbSession, get_current_user, require_roles
from app.models.domain import (
    Domain,
    StudentDomain,
    StudentTechnology,
    Technology,
)
from app.models.student import Student
from app.models.user import User
from app.schemas.student import (
    DomainItem,
    StudentCreate,
    StudentResponse,
    StudentUpdate,
    TechnologyItem,
)
from app.utils.enums import UserRole

router = APIRouter(prefix="/students", tags=["students"])

StudentOnly = Annotated[
    User,
    Depends(require_roles(UserRole.STUDENT)),
]


def _sync_student_domains(
    db: Session,
    student: Student,
    domains: list[DomainItem],
) -> None:
    """Synchronize a student's domains and technologies."""
    student.domains.clear()
    db.flush()

    for item in domains:
        domain = db.scalar(select(Domain).where(Domain.name == item.domain))
        if domain is None:
            domain = Domain(name=item.domain)
            db.add(domain)
            db.flush()

        student_domain = StudentDomain(
            student_id=student.id,
            domain_id=domain.id,
        )
        db.add(student_domain)
        db.flush()

        selected = set()
        for tech_item in item.technologies:
            if tech_item.technology in selected:
                continue
            technology = db.scalar(
                select(Technology).where(
                    Technology.domain_id == domain.id,
                    Technology.name == tech_item.technology,
                )
            )
            if technology is None:
                technology = Technology(
                    domain_id=domain.id,
                    name=tech_item.technology,
                )
                db.add(technology)
                db.flush()
            student_domain.technologies.append(
                StudentTechnology(technology_id=technology.id)
            )
            selected.add(tech_item.technology)


def _student_response(student: Student, user: User) -> StudentResponse:
    domain_items = []
    for sd in student.domains:
        tech_items = [
            TechnologyItem(technology=st.technology.name)
            for st in sd.technologies
            if st.technology is not None
        ]
        domain_items.append(
            DomainItem(domain=sd.domain.name, technologies=tech_items)
        )
    return StudentResponse(
        id=student.id,
        student_id=student.student_id,
        user_id=user.id,
        user_full_name=user.full_name or "",
        user_email=user.email,
        department=student.department,
        phone=student.phone,
        github_url=student.github_url,
        linkedin_url=student.linkedin_url,
        portfolio_url=student.portfolio_url,
        domains=domain_items,
        created_at=student.created_at,
        updated_at=student.updated_at,
    )


@router.get("/me", response_model=StudentResponse)
def get_my_profile(
    db: DbSession,
    current_user: StudentOnly,
) -> StudentResponse:
    """Fetch the authenticated student's profile."""
    stmt = (
        select(Student)
        .where(Student.user_id == current_user.id)
        .options(
            selectinload(Student.domains)
            .selectinload(StudentDomain.domain),
            selectinload(Student.domains)
            .selectinload(StudentDomain.technologies)
            .selectinload(StudentTechnology.technology),
        )
    )
    student = db.scalar(stmt)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )
    return _student_response(student, current_user)


@router.post("/me", response_model=StudentResponse)
def create_or_update_my_profile(
    payload: StudentCreate,
    db: DbSession,
    current_user: StudentOnly,
) -> StudentResponse:
    """Create or replace the authenticated student's profile."""
    stmt = (
        select(Student)
        .where(Student.user_id == current_user.id)
        .options(
            selectinload(Student.domains)
            .selectinload(StudentDomain.domain),
            selectinload(Student.domains)
            .selectinload(StudentDomain.technologies)
            .selectinload(StudentTechnology.technology),
        )
    )
    student = db.scalar(stmt)

    if payload.name:
        current_user.full_name = payload.name

    if student is None:
        # Check student_id uniqueness
        existing_with_id = db.scalar(
            select(Student).where(Student.student_id == payload.student_id)
        )
        if existing_with_id is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Student ID is already registered by another account",
            )
        student = Student(
            user_id=current_user.id,
            student_id=payload.student_id,
            department=payload.department,
            phone=payload.phone,
            github_url=payload.github_url,
            linkedin_url=payload.linkedin_url,
            portfolio_url=payload.portfolio_url,
        )
        db.add(student)
        db.flush()
    else:
        if student.student_id != payload.student_id:
            existing_with_id = db.scalar(
                select(Student).where(
                    Student.student_id == payload.student_id,
                    Student.id != student.id,
                )
            )
            if existing_with_id is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Student ID is already registered by another account",
                )
            student.student_id = payload.student_id

        student.department = payload.department
        student.phone = payload.phone
        student.github_url = payload.github_url
        student.linkedin_url = payload.linkedin_url
        student.portfolio_url = payload.portfolio_url

    _sync_student_domains(db, student, payload.domains)

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save student profile",
        ) from exc

    db.refresh(student)
    return _student_response(student, current_user)


@router.patch("/me", response_model=StudentResponse)
def patch_my_profile(
    payload: StudentUpdate,
    db: DbSession,
    current_user: StudentOnly,
) -> StudentResponse:
    """Partially update the authenticated student's profile."""
    stmt = (
        select(Student)
        .where(Student.user_id == current_user.id)
        .options(
            selectinload(Student.domains)
            .selectinload(StudentDomain.domain),
            selectinload(Student.domains)
            .selectinload(StudentDomain.technologies)
            .selectinload(StudentTechnology.technology),
        )
    )
    student = db.scalar(stmt)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    if payload.name is not None:
        current_user.full_name = payload.name

    if payload.student_id is not None and payload.student_id != student.student_id:
        existing_with_id = db.scalar(
            select(Student).where(
                Student.student_id == payload.student_id,
                Student.id != student.id,
            )
        )
        if existing_with_id is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Student ID is already registered by another account",
            )
        student.student_id = payload.student_id

    if payload.department is not None:
        student.department = payload.department
    if payload.phone is not None:
        student.phone = payload.phone
    if payload.github_url is not None:
        student.github_url = payload.github_url
    if payload.linkedin_url is not None:
        student.linkedin_url = payload.linkedin_url
    if payload.portfolio_url is not None:
        student.portfolio_url = payload.portfolio_url

    if payload.domains is not None:
        _sync_student_domains(db, student, payload.domains)

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update student profile",
        ) from exc

    db.refresh(student)
    return _student_response(student, current_user)
