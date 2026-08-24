"""Campus Bounties endpoints.

- ``POST   /bounties``                              - create a bounty (club admin only).
- ``PATCH  /bounties/{bounty_id}``                  - update a bounty (club admin only).
- ``GET    /bounties/{bounty_id}``                  - fetch a bounty (authenticated user).
- ``DELETE /bounties/{bounty_id}``                  - delete a bounty (club admin only).
- ``POST   /bounties/{bounty_id}/applications``     - apply to a bounty (student only).
- ``GET    /applications/{application_id}``         - fetch an application (club admin or owner).
- ``PATCH  /applications/{application_id}``         - update application status (club admin only).
- ``DELETE /applications/{application_id}``         - delete own rejected application (owner student only).
- ``POST   /applications/{application_id}/work``    - assign work to an accepted application (club admin only).
- ``GET    /applications/{application_id}/work``    - fetch assigned work (club admin or owner).
- ``PATCH  /applications/{application_id}/work``    - update work (admin or owner, role-scoped fields).
- ``GET    /students/me/skills``                    - fetch the authenticated student's skills.
"""

from __future__ import annotations

import uuid
import base64
import io
from typing import Annotated

from fastapi import APIRouter, Body, Depends, File, HTTPException, UploadFile, status
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.api.deps import DbSession, get_current_user, require_roles
from app.models.bounty import (
    Application,
    Bounty,
    BountyTechnology,
    Deliverable,
    Responsibility,
    Work,
)
from app.models.domain import (
    Domain,
    StudentDomain,
    StudentTechnology,
    Technology,
)
from app.models.event import Event
from app.models.student import Student
from app.models.user import User
from app.schemas.bounty import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationSummary,
    ApplicationUpdate,
    BountyCreate,
    BountyResponse,
    BountyUpdate,
    DeliverableResponse,
    DeliverableStatusItem,
    DomainInfo,
    EventInfo,
    ResponsibilityItem,
    StudentInfo,
    TechnologyItem,
    WorkCreate,
    WorkResponse,
    WorkUpdateByAdmin,
    WorkUpdateByStudent,
)
from app.schemas.student import DomainItem
from app.schemas.student import TechnologyItem as StudentTechnologyItem
from app.utils.enums import (
    ApplicationStatus,
    BountyStatus,
    DomainEnum,
    TechnologyEnum,
    UserRole,
    WorkStatus,
)

router = APIRouter()

CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]

ClubAdmin = Annotated[
    User,
    Depends(require_roles(UserRole.CLUB_ADMIN))
]

StudentOnly = Annotated[
    User,
    Depends(require_roles(UserRole.STUDENT))
]

AdminOrStudent = Annotated[
    User,
    Depends(require_roles(UserRole.CLUB_ADMIN, UserRole.STUDENT))
]


def _get_current_student(db: DbSession, current_user: User) -> Student:
    """Resolve the Student profile linked to the authenticated user."""
    student = db.scalar(select(Student).where(Student.user_id == current_user.id))
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )
    return student


def _load_bounty(db: DbSession, bounty_id: uuid.UUID) -> Bounty | None:
    """Load a bounty with everything needed for a full response."""
    return db.scalar(
        select(Bounty)
        .where(Bounty.id == bounty_id)
        .options(
            selectinload(Bounty.domain),
            selectinload(Bounty.technologies).selectinload(
                BountyTechnology.technology
            ),
            selectinload(Bounty.responsibilities),
            selectinload(Bounty.created_by_user),
        )
    )


def _bounty_response(bounty: Bounty) -> BountyResponse:
    """Build the full bounty response with its related entities."""
    return BountyResponse(
        id=bounty.id,
        title=bounty.title,
        domain=DomainInfo(id=bounty.domain.id, name=bounty.domain.name),
        description=bounty.description,
        reward=bounty.reward,
        application_deadline=bounty.application_deadline,
        duration=bounty.duration,
        student_seats=bounty.student_seats,
        image_url=bounty.image_url,
        status=bounty.status,
        technologies=[
            TechnologyItem(id=link.technology.id, name=link.technology.name)
            for link in bounty.technologies
        ],
        responsibilities=[
            ResponsibilityItem(id=item.id, title=item.title)
            for item in bounty.responsibilities
        ],
        created_by=bounty.created_by,
        created_by_name=bounty.created_by_user.full_name
        if bounty.created_by_user is not None
        else None,
        created_at=bounty.created_at,
        updated_at=bounty.updated_at,
    )


def _validate_technologies(
    db: DbSession,
    technology_ids: list[uuid.UUID],
) -> None:
    """Ensure every technology exists in the database."""
    for technology_id in technology_ids:
        technology = db.get(Technology, technology_id)
        if technology is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technology not found",
            )


def _load_application(db: DbSession, application_id: uuid.UUID) -> Application | None:
    """Load an application with its bounty, student and skill relations."""
    return db.scalar(
        select(Application)
        .where(Application.id == application_id)
        .options(
            selectinload(Application.bounty).selectinload(Bounty.domain),
            selectinload(Application.bounty)
            .selectinload(Bounty.technologies)
            .selectinload(BountyTechnology.technology),
            selectinload(Application.bounty).selectinload(Bounty.responsibilities),
            selectinload(Application.bounty).selectinload(Bounty.created_by_user),
            selectinload(Application.student).selectinload(Student.user),
            selectinload(Application.student)
            .selectinload(Student.domains)
            .selectinload(StudentDomain.technologies)
            .selectinload(StudentTechnology.technology),
        )
    )


def _student_info(student: Student) -> StudentInfo:
    """Build the student info embedded in an application response."""
    return StudentInfo(
        id=student.id,
        name=student.user.full_name,
        email=student.user.email,
        student_id=student.student_id,
        department=student.department,
    )


def _matched_technologies(application: Application) -> list[TechnologyEnum]:
    """Intersection of the bounty's required and the student's declared
    technologies."""
    bounty_technologies = {
        link.technology.name for link in application.bounty.technologies
    }
    student_technologies: set[TechnologyEnum] = set()
    for student_domain in application.student.domains:
        for link in student_domain.technologies:
            student_technologies.add(link.technology.name)
    return [name for name in bounty_technologies if name in student_technologies]


def _application_response(application: Application) -> ApplicationResponse:
    """Build the full application response."""
    return ApplicationResponse(
        id=application.id,
        bounty_id=application.bounty_id,
        student_id=application.student_id,
        availability=application.availability,
        resume=application.resume,
        status=application.status,
        created_at=application.created_at,
        updated_at=application.updated_at,
        bounty=_bounty_response(application.bounty),
        student=_student_info(application.student),
        matched_technologies=_matched_technologies(application),
    )


def _load_work(db: DbSession, application_id: uuid.UUID) -> Work | None:
    """Load the work of an application with its related entities."""
    return db.scalar(
        select(Work)
        .where(Work.application_id == application_id)
        .options(
            selectinload(Work.deliverables),
            selectinload(Work.event),
            selectinload(Work.application).selectinload(Application.bounty),
            selectinload(Work.application)
            .selectinload(Application.student)
            .selectinload(Student.user),
        )
    )


def _work_response(work: Work) -> WorkResponse:
    """Build the full assigned-work response."""
    application = work.application
    return WorkResponse(
        id=work.id,
        application_id=work.application_id,
        title=work.title,
        task_description=work.task_description,
        deadline=work.deadline,
        event_id=work.event_id,
        status=work.status,
        created_at=work.created_at,
        updated_at=work.updated_at,
        deliverables=[
            DeliverableResponse(
                id=deliverable.id,
                work_id=deliverable.work_id,
                title=deliverable.title,
                status=deliverable.status,
            )
            for deliverable in work.deliverables
        ],
        event=EventInfo(id=work.event.id, name=work.event.name)
        if work.event is not None
        else None,
        application=ApplicationSummary(
            id=application.id,
            bounty_id=application.bounty_id,
            student_id=application.student_id,
            status=application.status,
            bounty_title=application.bounty.title,
            student_name=application.student.user.full_name,
        ),
    )


def _update_deliverable_statuses(
    db: DbSession,
    work: Work,
    deliverables: list[DeliverableStatusItem],
) -> None:
    """Apply status updates to the work's deliverables keyed by id."""
    work_deliverables = {deliverable.id: deliverable for deliverable in work.deliverables}
    for item in deliverables:
        deliverable = work_deliverables.get(item.id)
        if deliverable is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deliverable not found",
            )
        deliverable.status = item.status


def _validate_event(db: DbSession, event_id: uuid.UUID | None) -> None:
    if event_id is not None and db.get(Event, event_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )


# ---------------------------------------------------------------- Bounty
@router.get(
    "/bounties",
    response_model=list[BountyResponse],
)
def list_bounties(
    db: DbSession,
    status: BountyStatus | None = None,
    domain_id: uuid.UUID | None = None,
) -> list[BountyResponse]:
    """Fetch all bounties with nested domains, technologies, and responsibilities."""
    stmt = (
        select(Bounty)
        .options(
            selectinload(Bounty.domain),
            selectinload(Bounty.technologies).selectinload(BountyTechnology.technology),
            selectinload(Bounty.responsibilities),
            selectinload(Bounty.created_by_user),
        )
        .order_by(Bounty.created_at.desc())
    )
    if status is not None:
        stmt = stmt.where(Bounty.status == status)
    if domain_id is not None:
        stmt = stmt.where(Bounty.domain_id == domain_id)
    bounties = list(db.scalars(stmt))
    return [_bounty_response(b) for b in bounties]


@router.post(
    "/bounties",
    response_model=BountyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_bounty(
    payload: BountyCreate,
    db: DbSession,
    current_user: ClubAdmin,
) -> BountyResponse:
    """Create a bounty together with its technologies and responsibilities."""
    if db.get(Domain, payload.domain_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found",
        )
    _validate_technologies(db, payload.technologies)

    bounty = Bounty(
        title=payload.title,
        domain_id=payload.domain_id,
        description=payload.description,
        reward=payload.reward,
        application_deadline=payload.application_deadline,
        duration=payload.duration,
        student_seats=payload.student_seats,
        image_url=payload.image_url,
        status=BountyStatus.OPEN,
        created_by=current_user.id,
    )
    db.add(bounty)
    try:
        db.flush()
        for technology_id in payload.technologies:
            db.add(
                BountyTechnology(
                    bounty_id=bounty.id,
                    technology_id=technology_id,
                )
            )
        for title in payload.responsibilities:
            db.add(
                Responsibility(
                    bounty_id=bounty.id,
                    title=title,
                )
            )
        db.commit()
    except Exception as exc:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create bounty: {exc}",
        ) from exc

    created_bounty = _load_bounty(db, bounty.id)
    if created_bounty is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load created bounty",
        )
    return _bounty_response(created_bounty)


@router.patch("/bounties/{bounty_id}", response_model=BountyResponse)
def update_bounty(
    bounty_id: uuid.UUID,
    payload: BountyUpdate,
    db: DbSession,
    current_user: ClubAdmin,
) -> BountyResponse:
    """Update a bounty, replacing supplied technology/responsibility lists
    wholesale."""
    bounty = _load_bounty(db, bounty_id)
    if bounty is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bounty not found",
        )

    update_data = payload.model_dump(exclude_unset=True)
    technologies = update_data.pop("technologies", None)
    responsibilities = update_data.pop("responsibilities", None)

    new_domain_id = update_data.get("domain_id")
    if new_domain_id is not None:
        if db.get(Domain, new_domain_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain not found",
            )
        domain_id = new_domain_id
    else:
        domain_id = bounty.domain_id

    if technologies is not None:
        _validate_technologies(db, technologies)

    for field, value in update_data.items():
        setattr(bounty, field, value)

    if technologies is not None:
        bounty.technologies = [
            BountyTechnology(technology_id=technology_id)
            for technology_id in technologies
        ]
    if responsibilities is not None:
        bounty.responsibilities = [
            Responsibility(title=title) for title in responsibilities
        ]

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update bounty",
        ) from exc

    updated_bounty = _load_bounty(db, bounty.id)
    if updated_bounty is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load updated bounty",
        )
    return _bounty_response(updated_bounty)


@router.get("/bounties/{bounty_id}", response_model=BountyResponse)
def get_bounty(
    bounty_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> BountyResponse:
    """Fetch the full bounty information for any authenticated user."""
    bounty = _load_bounty(db, bounty_id)
    if bounty is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bounty not found",
        )
    return _bounty_response(bounty)


@router.delete("/bounties/{bounty_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bounty(
    bounty_id: uuid.UUID,
    db: DbSession,
    current_user: ClubAdmin,
) -> None:
    """Delete a bounty; related rows cascade via the model configuration."""
    bounty = db.get(Bounty, bounty_id)
    if bounty is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bounty not found",
        )
    db.delete(bounty)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete bounty",
        ) from exc


# ----------------------------------------------------------- Application
@router.post(
    "/bounties/{bounty_id}/applications",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_application(
    bounty_id: uuid.UUID,
    payload: ApplicationCreate,
    db: DbSession,
    current_user: StudentOnly,
) -> ApplicationResponse:
    """Apply to a bounty as the authenticated student."""
    bounty = db.get(Bounty, bounty_id)
    if bounty is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bounty not found",
        )
    if bounty.status != BountyStatus.OPEN:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bounty is not accepting applications",
        )

    student = _get_current_student(db, current_user)
    existing = db.scalar(
        select(Application).where(
            Application.bounty_id == bounty_id,
            Application.student_id == student.id,
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already applied to this bounty",
        )

    application = Application(
        bounty_id=bounty_id,
        student_id=student.id,
        availability=payload.availability,
        resume=payload.resume,
        status=ApplicationStatus.PENDING,
    )
    db.add(application)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create application",
        ) from exc

    created_application = _load_application(db, application.id)
    if created_application is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load created application",
        )
    return _application_response(created_application)


@router.get(
    "/bounties/{bounty_id}/applications",
    response_model=list[ApplicationResponse],
)
def list_bounty_applications(
    bounty_id: uuid.UUID,
    db: DbSession,
    current_user: ClubAdmin,
) -> list[ApplicationResponse]:
    """List all applications submitted for a bounty (club admin only)."""
    applications = list(
        db.scalars(
            select(Application)
            .where(Application.bounty_id == bounty_id)
            .options(
                selectinload(Application.bounty).selectinload(Bounty.domain),
                selectinload(Application.bounty)
                .selectinload(Bounty.technologies)
                .selectinload(BountyTechnology.technology),
                selectinload(Application.bounty).selectinload(Bounty.responsibilities),
                selectinload(Application.bounty).selectinload(Bounty.created_by_user),
                selectinload(Application.student).selectinload(Student.user),
                selectinload(Application.student)
                .selectinload(Student.domains)
                .selectinload(StudentDomain.technologies)
                .selectinload(StudentTechnology.technology),
                selectinload(Application.work).selectinload(Work.deliverables),
            )
            .order_by(Application.created_at.desc())
        )
    )
    return [_application_response(a) for a in applications]


@router.get(
    "/applications/me",
    response_model=list[ApplicationResponse],
)
def get_my_applications(
    db: DbSession,
    current_user: StudentOnly,
) -> list[ApplicationResponse]:
    """Fetch the authenticated student's applications."""
    student = _get_current_student(db, current_user)
    applications = list(
        db.scalars(
            select(Application)
            .where(Application.student_id == student.id)
            .options(
                selectinload(Application.bounty).selectinload(Bounty.domain),
                selectinload(Application.bounty)
                .selectinload(Bounty.technologies)
                .selectinload(BountyTechnology.technology),
                selectinload(Application.bounty).selectinload(Bounty.responsibilities),
                selectinload(Application.bounty).selectinload(Bounty.created_by_user),
                selectinload(Application.student).selectinload(Student.user),
                selectinload(Application.student)
                .selectinload(Student.domains)
                .selectinload(StudentDomain.technologies)
                .selectinload(StudentTechnology.technology),
                selectinload(Application.work).selectinload(Work.deliverables),
            )
            .order_by(Application.created_at.desc())
        )
    )
    return [_application_response(a) for a in applications]


@router.get("/applications/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: uuid.UUID,
    db: DbSession,
    current_user: AdminOrStudent,
) -> ApplicationResponse:
    """Fetch an application; the admin sees any, a student only their own."""
    application = _load_application(db, application_id)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    if current_user.role == UserRole.STUDENT:
        student = _get_current_student(db, current_user)
        if application.student_id != student.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to view this application",
            )
    return _application_response(application)


@router.delete(
    "/applications/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_rejected_application(
    application_id: uuid.UUID,
    db: DbSession,
    current_user: StudentOnly,
) -> None:
    """Delete the authenticated student's own application, but only once it has
    been rejected."""
    student = _get_current_student(db, current_user)

    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    if application.student_id != student.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete this application",
        )
    if application.status != ApplicationStatus.REJECTED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only a rejected application can be deleted",
        )

    db.delete(application)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete application",
        ) from exc


@router.patch("/applications/{application_id}", response_model=ApplicationResponse)
def update_application_status(
    application_id: uuid.UUID,
    payload: ApplicationUpdate,
    db: DbSession,
    current_user: ClubAdmin,
) -> ApplicationResponse:
    """Update an application's status (club admin only), respecting the seat
    limit when accepting."""
    application = _load_application(db, application_id)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    if (
        payload.status == ApplicationStatus.ACCEPTED
        and application.status != ApplicationStatus.ACCEPTED
    ):
        accepted_count = (
            db.scalar(
                select(func.count())
                .select_from(Application)
                .where(
                    Application.bounty_id == application.bounty_id,
                    Application.status == ApplicationStatus.ACCEPTED,
                    Application.id != application.id,
                )
            )
            or 0
        )
        if accepted_count >= application.bounty.student_seats:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="All seats for this bounty are filled",
            )

    application.status = payload.status
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update application",
        ) from exc

    updated_application = _load_application(db, application.id)
    if updated_application is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load updated application",
        )
    return _application_response(updated_application)


# ---------------------------------------------------------------- Work
@router.post(
    "/applications/{application_id}/work",
    response_model=WorkResponse,
    status_code=status.HTTP_201_CREATED,
)
def assign_work(
    application_id: uuid.UUID,
    payload: WorkCreate,
    db: DbSession,
    current_user: ClubAdmin,
) -> WorkResponse:
    """Assign work to an accepted application, creating its deliverables."""
    application = db.scalar(
        select(Application)
        .where(Application.id == application_id)
        .options(selectinload(Application.work))
    )
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    if application.status != ApplicationStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only an accepted application can receive work",
        )
    if application.work is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Work is already assigned to this application",
        )
    _validate_event(db, payload.event_id)

    work = Work(
        application_id=application.id,
        title=payload.title,
        task_description=payload.task_description,
        deadline=payload.deadline,
        event_id=payload.event_id,
        status=WorkStatus.ASSIGNED,
    )
    db.add(work)
    try:
        db.flush()
        work.deliverables = [
            Deliverable(title=item.title) for item in payload.deliverables
        ]
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign work",
        ) from exc

    created_work = _load_work(db, application.id)
    if created_work is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load assigned work",
        )
    return _work_response(created_work)


@router.get("/applications/{application_id}/work", response_model=WorkResponse)
def get_assigned_work(
    application_id: uuid.UUID,
    db: DbSession,
    current_user: AdminOrStudent,
) -> WorkResponse:
    """Fetch the work of an application; admin sees any, student only their
    own."""
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    work = _load_work(db, application_id)
    if work is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work not found for this application",
        )
    if current_user.role == UserRole.STUDENT:
        student = _get_current_student(db, current_user)
        if application.student_id != student.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to view this work",
            )
    return _work_response(work)


@router.patch("/applications/{application_id}/work", response_model=WorkResponse)
def update_assigned_work(
    application_id: uuid.UUID,
    payload: Annotated[
        dict,
        Body(
            ...,
            examples=[
                {
                    "status": "in_progress",
                    "deliverables": [{"id": "00000000-0000-0000-0000-000000000001", "status": "completed"}],
                }
            ],
        ),
    ],
    db: DbSession,
    current_user: AdminOrStudent,
) -> WorkResponse:
    """Update work. The allowed fields depend on the caller's role: a student
    may only update progress (work status and deliverable statuses), while the
    club admin may also edit the work details."""
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    work = _load_work(db, application_id)
    if work is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work not found for this application",
        )

    SchemaT: type[WorkUpdateByStudent | WorkUpdateByAdmin]
    if current_user.role == UserRole.STUDENT:
        student = _get_current_student(db, current_user)
        if application.student_id != student.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to update this work",
            )
        SchemaT = WorkUpdateByStudent
    else:
        SchemaT = WorkUpdateByAdmin

    try:
        parsed = SchemaT.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(),
        ) from exc

    update_data = parsed.model_dump(
        exclude_unset=True, exclude={"deliverables"}
    )
    deliverables = parsed.deliverables

    if current_user.role == UserRole.STUDENT:
        if "status" in update_data:
            work.status = update_data["status"]
    else:
        if "event_id" in update_data:
            _validate_event(db, update_data["event_id"])
        for field, value in update_data.items():
            setattr(work, field, value)

    if deliverables is not None:
        _update_deliverable_statuses(db, work, deliverables)

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update work",
        ) from exc

    updated_work = _load_work(db, application_id)
    if updated_work is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load updated work",
        )
    return _work_response(updated_work)


# ---------------------------------------------------------- Student skills
def _student_domain_items(student: Student) -> list[DomainItem]:
    """Build the student's skill hierarchy grouped by domain."""
    items: list[DomainItem] = []
    for student_domain in student.domains:
        items.append(
            DomainItem(
                domain=student_domain.domain.name,
                technologies=[
                    StudentTechnologyItem(technology=link.technology.name)
                    for link in student_domain.technologies
                ],
            )
        )
    return items


@router.get("/students/me/skills", response_model=list[DomainItem])
def get_my_skills(
    db: DbSession,
    current_user: StudentOnly,
) -> list[DomainItem]:
    """Fetch the authenticated student's declared skills (StudentTechnology)
    grouped by domain."""
    student = db.scalar(
        select(Student)
        .where(Student.user_id == current_user.id)
        .options(
            selectinload(Student.domains).selectinload(StudentDomain.domain),
            selectinload(Student.domains)
            .selectinload(StudentDomain.technologies)
            .selectinload(StudentTechnology.technology),
        )
    )
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )
    return _student_domain_items(student)


@router.get(
    "/work/me",
    response_model=list[WorkResponse],
)
def get_my_work(
    db: DbSession,
    current_user: StudentOnly,
) -> list[WorkResponse]:
    """Fetch all assigned work/volunteering tasks for the authenticated student."""
    student = _get_current_student(db, current_user)
    work_list = list(
        db.scalars(
            select(Work)
            .join(Application, Work.application_id == Application.id)
            .where(Application.student_id == student.id)
            .options(
                selectinload(Work.deliverables),
                selectinload(Work.event),
                selectinload(Work.application).selectinload(Application.bounty),
                selectinload(Work.application)
                .selectinload(Application.student)
                .selectinload(Student.user),
            )
            .order_by(Work.created_at.desc())
        )
    )
    return [_work_response(w) for w in work_list]


DOMAIN_TECHNOLOGY_MAPPING: dict[DomainEnum, list[TechnologyEnum]] = {
    DomainEnum.PROGRAMMING_LANGUAGES: [
        TechnologyEnum.PYTHON, TechnologyEnum.JAVA, TechnologyEnum.C, TechnologyEnum.CPP,
        TechnologyEnum.C_SHARP, TechnologyEnum.JAVASCRIPT, TechnologyEnum.TYPESCRIPT,
        TechnologyEnum.GO, TechnologyEnum.RUST, TechnologyEnum.PHP, TechnologyEnum.KOTLIN,
        TechnologyEnum.SWIFT, TechnologyEnum.DART, TechnologyEnum.R,
    ],
    DomainEnum.WEB_DEVELOPMENT: [
        TechnologyEnum.HTML, TechnologyEnum.CSS, TechnologyEnum.TAILWIND_CSS,
        TechnologyEnum.BOOTSTRAP, TechnologyEnum.REACT, TechnologyEnum.NEXT_JS,
        TechnologyEnum.VUE_JS, TechnologyEnum.NUXT_JS, TechnologyEnum.ANGULAR, TechnologyEnum.SVELTE,
    ],
    DomainEnum.BACKEND_DEVELOPMENT: [
        TechnologyEnum.NODE_JS, TechnologyEnum.EXPRESS_JS, TechnologyEnum.FASTAPI,
        TechnologyEnum.FLASK, TechnologyEnum.DJANGO, TechnologyEnum.SPRING_BOOT,
        TechnologyEnum.NEST_JS, TechnologyEnum.LARAVEL, TechnologyEnum.ASP_NET,
        TechnologyEnum.GRAPHQL, TechnologyEnum.REST_API,
    ],
    DomainEnum.APP_DEVELOPMENT: [
        TechnologyEnum.FLUTTER, TechnologyEnum.REACT_NATIVE, TechnologyEnum.ANDROID,
        TechnologyEnum.JETPACK_COMPOSE, TechnologyEnum.SWIFT_UI,
    ],
    DomainEnum.AI_ML: [
        TechnologyEnum.NUMPY, TechnologyEnum.PANDAS, TechnologyEnum.SCIKIT_LEARN,
        TechnologyEnum.TENSORFLOW, TechnologyEnum.PYTORCH, TechnologyEnum.KERAS,
        TechnologyEnum.OPENCV, TechnologyEnum.LANGCHAIN, TechnologyEnum.HUGGING_FACE,
        TechnologyEnum.OPENAI_API,
    ],
    DomainEnum.DATA_SCIENCE: [
        TechnologyEnum.MATPLOTLIB, TechnologyEnum.SEABORN, TechnologyEnum.POWER_BI,
        TechnologyEnum.TABLEAU, TechnologyEnum.JUPYTER,
    ],
    DomainEnum.CYBER_SECURITY: [
        TechnologyEnum.KALI_LINUX, TechnologyEnum.WIRESHARK, TechnologyEnum.BURP_SUITE,
        TechnologyEnum.NMAP, TechnologyEnum.METASPLOIT, TechnologyEnum.OWASP,
    ],
    DomainEnum.CLOUD_COMPUTING: [
        TechnologyEnum.AWS, TechnologyEnum.AZURE, TechnologyEnum.GOOGLE_CLOUD,
        TechnologyEnum.FIREBASE, TechnologyEnum.SUPABASE,
    ],
    DomainEnum.DEVOPS: [
        TechnologyEnum.DOCKER, TechnologyEnum.KUBERNETES, TechnologyEnum.JENKINS,
        TechnologyEnum.GITHUB_ACTIONS, TechnologyEnum.TERRAFORM, TechnologyEnum.ANSIBLE,
        TechnologyEnum.NGINX, TechnologyEnum.LINUX,
    ],
    DomainEnum.DATABASE: [
        TechnologyEnum.POSTGRESQL, TechnologyEnum.MYSQL, TechnologyEnum.SQLITE,
        TechnologyEnum.MONGODB, TechnologyEnum.REDIS, TechnologyEnum.ORACLE, TechnologyEnum.SQL_SERVER,
    ],
    DomainEnum.UI_UX_DESIGN: [
        TechnologyEnum.FIGMA, TechnologyEnum.ADOBE_XD, TechnologyEnum.CANVA,
        TechnologyEnum.PHOTOSHOP, TechnologyEnum.ILLUSTRATOR,
    ],
    DomainEnum.ROBOTICS: [
        TechnologyEnum.ROS, TechnologyEnum.ARDUINO, TechnologyEnum.RASPBERRY_PI,
    ],
    DomainEnum.IOT: [
        TechnologyEnum.ESP32, TechnologyEnum.MQTT,
    ],
    DomainEnum.BLOCKCHAIN: [
        TechnologyEnum.SOLIDITY, TechnologyEnum.HARDHAT, TechnologyEnum.FOUNDRY,
        TechnologyEnum.ETHERS_JS, TechnologyEnum.WEB3_JS,
    ],
    DomainEnum.GAME_DEVELOPMENT: [
        TechnologyEnum.UNITY, TechnologyEnum.UNREAL_ENGINE, TechnologyEnum.GODOT, TechnologyEnum.BLENDER,
    ],
    DomainEnum.COMPETITIVE_PROGRAMMING: [
        TechnologyEnum.CODEFORCES, TechnologyEnum.CODECHEF, TechnologyEnum.LEETCODE,
        TechnologyEnum.ATCODER, TechnologyEnum.HACKERRANK,
    ],
}


def _ensure_domains_and_techs_seeded(db: DbSession) -> None:
    """Ensure all DomainEnum and TechnologyEnum records are seeded in DB."""
    try:
        for domain_enum, tech_enums in DOMAIN_TECHNOLOGY_MAPPING.items():
            domain = db.scalar(
                select(Domain)
                .where(Domain.name == domain_enum)
                .options(selectinload(Domain.technologies))
            )
            if domain is None:
                domain = Domain(name=domain_enum)
                db.add(domain)
                db.flush()
                existing_tech_names = set()
            else:
                existing_tech_names = {t.name for t in domain.technologies}

            for tech_enum in tech_enums:
                if tech_enum not in existing_tech_names:
                    tech = Technology(domain_id=domain.id, name=tech_enum)
                    db.add(tech)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[Domains Seeder Warning] {e}")


@router.get(
    "/domains",
)
def list_domains(
    db: DbSession,
):
    """Fetch all domains and their associated technologies."""
    _ensure_domains_and_techs_seeded(db)
    domains = list(
        db.scalars(
            select(Domain)
            .options(selectinload(Domain.technologies))
            .order_by(Domain.name)
        )
    )
    return [
        {
            "id": str(d.id),
            "name": d.name.value if hasattr(d.name, "value") else str(d.name),
            "technologies": [
                {
                    "id": str(t.id),
                    "name": t.name.value if hasattr(t.name, "value") else str(t.name),
                }
                for t in d.technologies
            ],
        }
        for d in domains
    ]


@router.post("/bounties/upload-image")
async def upload_bounty_image(
    current_user: ClubAdmin,
    file: UploadFile = File(...),
) -> dict[str, str]:
    """Upload a bounty image to Cloudinary and return secure URL."""
    try:
        from app.core.config import settings
        content = await file.read()
        if settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET:
            import cloudinary
            import cloudinary.uploader

            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
            )
            upload_result = cloudinary.uploader.upload(
                io.BytesIO(content),
                folder="club-management/bounties",
                resource_type="image",
                overwrite=True,
            )
            secure_url = upload_result.get("secure_url")
            if secure_url:
                return {"image_url": secure_url}
        # Fallback to data URI if Cloudinary is not configured
        b64 = base64.b64encode(content).decode("utf-8")
        mime = file.content_type or "image/png"
        return {"image_url": f"data:{mime};base64,{b64}"}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image upload failed: {exc}",
        )