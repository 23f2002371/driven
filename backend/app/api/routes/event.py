"""Event endpoints.

- ``POST   /events``                          - create an event (club/lab admin only).
- ``PATCH  /events/{event_id}``               - update an event (club/lab admin only).
- ``GET    /events/{event_id}``               - fetch the public event page.
- ``GET    /events/{event_id}/private``       - fetch the full event for the admin dashboard.
- ``POST   /events/registrations``            - register the student for an event.
- ``PATCH  /events/registrations/{id}``       - update the student's own registration.
- ``GET    /events/registrations/{id}``       - fetch the student's own registration.
- ``POST   /events/winners``                  - declare a winner (club admin only).
- ``PUT    /events/winners``                  - upsert all winner positions (club admin only).
- ``GET    /events/{event_id}/winners``       - fetch all winners of an event (public).
- ``POST   /events/{event_id}/certificates``  - generate certificates (club admin only).
- ``GET    /students/{student_id}/certificates`` - fetch a student's certificates (student only).
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import String, cast, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.api.deps import DbSession, get_current_user, require_roles
from app.core.config import settings
from app.models.domain import (
    Domain,
    StudentDomain,
    StudentTechnology,
    Technology,
)
from app.models.event import (
    AdditionalEventInfo,
    Certificate,
    Event,
    EventAgenda,
    EventMentor,
    EventRegistration,
    EventRejectReason,
    EventWinner,
)
from app.models.student import Student
from app.models.user import User
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
    RegistrationVerifyRequest,
    RegistrationVerifyResponse,
    StudentProfile,
)
from app.schemas.student import DomainItem, TechnologyItem
from app.services.qr import (
    extract_registration_id,
    extract_registration_identifier,
    generate_registration_qr_code,
)
from app.utils.enums import (
    AttendanceStatus,
    CertificateType,
    Department,
    EventRejectionReason,
    EventStatus,
    UserRole,
    WinnerPosition,
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

ClubOrLabAdmin = Annotated[
    User,
    Depends(require_roles(UserRole.CLUB_ADMIN, UserRole.LAB_ADMIN))
]

StudentOnly = Annotated[
    User,
    Depends(require_roles(UserRole.STUDENT))
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


def _student_domain_items(student: Student) -> list[DomainItem]:
    """Build the DomainItem hierarchy for a student."""
    items: list[DomainItem] = []
    for student_domain in student.domains:
        items.append(
            DomainItem(
                domain=student_domain.domain.name,
                technologies=[
                    TechnologyItem(technology=link.technology.name)
                    for link in student_domain.technologies
                ],
            )
        )
    return items


def _sync_student_domains(
    db: DbSession,
    student: Student,
    domains: list[DomainItem],
) -> None:
    """Attach the submitted domains (and their technologies) to a student.

    Reuses the student's existing domains instead of creating duplicates: a
    domain already present on the student is only extended with the missing
    technologies. Technologies that already exist inside a student-domain are
    never inserted again.
    """
    for item in domains:
        domain = db.scalar(select(Domain).where(Domain.name == item.domain))
        if domain is None:
            domain = Domain(name=item.domain)
            db.add(domain)
            db.flush()

        student_domain = db.scalar(
            select(StudentDomain).where(
                StudentDomain.student_id == student.id,
                StudentDomain.domain_id == domain.id,
            )
        )
        if student_domain is None:
            student_domain = StudentDomain(
                student_id=student.id,
                domain_id=domain.id,
            )
            db.add(student_domain)
            db.flush()

        selected = {
            relation.technology.name for relation in student_domain.technologies
        }
        for tech_item in item.technologies:
            if tech_item.technology in selected:
                continue
            technology = db.scalar(
                select(Technology)
                .where(
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


def _student_profile(student: Student) -> StudentProfile:
    """Build the submitted student information for a registration response."""
    return StudentProfile(
        name=student.user.full_name,
        email=student.user.email,
        student_id=student.student_id,
        department=student.department,
        phone=student.phone,
        github=student.github_url,
        linkedin=student.linkedin_url,
        portfolio=student.portfolio_url,
        domains=_student_domain_items(student),
    )


def _public_event_response(event: Event) -> EventResponse:
    """Build the public event representation for a registration response."""
    winner = next(
        (w for w in event.winners if w.position == WinnerPosition.FIRST),
        event.winners[0] if event.winners else None,
    )

    return EventResponse(
        id=event.id,
        name=event.name,
        short_description=event.short_description,
        category=event.category,
        event_date=event.event_date,
        venue=event.venue,
        max_participants=event.max_participants,
        description=event.description,
        cover_image_url=event.cover_image_url,
        winner_name=winner.project_name if winner else None,
        winner_project_url=winner.project_url if winner else None,
    )


def _registration_response(registration: EventRegistration) -> EventRegistrationResponse:
    """Build the full registration response, embedding the student information
    and the public event details."""
    return EventRegistrationResponse(
        id=registration.id,
        event_id=registration.event_id,
        student_id=registration.student_id,
        team_name=registration.team_name,
        qr_code_url=registration.qr_code_url,
        registration_status=registration.registration_status,
        attendance_status=registration.attendance_status,
        student=_student_profile(registration.student),
        event=_public_event_response(registration.event),
    )


def _registration_eager_loads():
    """Eager-load the nested student profile and public event details for
    registration responses."""
    return [
        selectinload(EventRegistration.student).selectinload(Student.domains)
        .selectinload(StudentDomain.technologies)
        .selectinload(StudentTechnology.technology),
        selectinload(EventRegistration.student).selectinload(Student.domains)
        .selectinload(StudentDomain.domain),
        selectinload(EventRegistration.event).selectinload(Event.winners),
    ]


def _certificate_response(certificate: Certificate) -> CertificateResponse:
    """Build the certificate response, including event and student names."""
    return CertificateResponse(
        id=certificate.id,
        event_id=certificate.event_id,
        student_id=certificate.student_id,
        registration_id=certificate.registration_id,
        certificate_type=certificate.certificate_type,
        issue_date=certificate.issue_date,
        certificate_url=certificate.certificate_url,
        event_name=certificate.event.name,
        student_name=certificate.student.user.full_name,
    )


_CERTIFICATE_TYPE_BY_POSITION: dict[WinnerPosition, CertificateType] = {
    WinnerPosition.FIRST: CertificateType.FIRST,
    WinnerPosition.SECOND: CertificateType.SECOND,
    WinnerPosition.THIRD: CertificateType.THIRD,
}


@router.post(
    "/events",
    response_model=PrivateEventResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_event(
    request: Request,
    db: DbSession,
    current_user: ClubAdmin,
) -> Event:
    """Create an event together with its agenda, additional info and mentors.
    Supports both multipart/form-data (with file upload) and application/json.
    """
    content_type = request.headers.get("content-type", "")

    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        name = form.get("name")
        short_description = form.get("short_description")
        category = form.get("category")
        event_date = form.get("event_date")
        registration_deadline = form.get("registration_deadline")
        venue = form.get("venue")
        max_participants = form.get("max_participants")
        description = form.get("description")
        cover_image_url = form.get("cover_image_url") or None

        agendas_raw = form.get("agendas")
        try:
            agendas = json.loads(agendas_raw) if agendas_raw else []
        except Exception:
            agendas = []

        additional_info_raw = form.get("additional_info")
        try:
            additional_info = json.loads(additional_info_raw) if additional_info_raw else []
        except Exception:
            additional_info = []

        mentors_raw = form.get("mentors")
        try:
            mentors = json.loads(mentors_raw) if mentors_raw else []
        except Exception:
            mentors = []

        # Handle image file upload to Cloudinary
        cover_image_file = form.get("cover_image")
        if cover_image_file and hasattr(cover_image_file, "file") and getattr(cover_image_file, "filename", None):
            if settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET:
                try:
                    import cloudinary
                    import cloudinary.uploader

                    cloudinary.config(
                        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                        api_key=settings.CLOUDINARY_API_KEY,
                        api_secret=settings.CLOUDINARY_API_SECRET,
                    )
                    file_bytes = await cover_image_file.read()
                    if file_bytes:
                        upload_result = cloudinary.uploader.upload(
                            file_bytes,
                            folder="club-management/events",
                            resource_type="image",
                        )
                        cover_image_url = upload_result.get("secure_url")
                except Exception:
                    pass

        payload_dict = {
            "name": name,
            "short_description": short_description,
            "category": category,
            "event_date": event_date,
            "registration_deadline": registration_deadline,
            "venue": venue,
            "max_participants": int(max_participants) if max_participants else 1,
            "description": description,
            "cover_image_url": cover_image_url,
            "agendas": agendas,
            "additional_info": additional_info,
            "mentors": mentors,
        }
        try:
            payload = EventCreate.model_validate(payload_dict)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc
    else:
        try:
            body = await request.json()
            payload = EventCreate.model_validate(body)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc

    event = Event(
        name=payload.name,
        short_description=payload.short_description,
        category=payload.category,
        event_date=payload.event_date,
        registration_deadline=payload.registration_deadline,
        venue=payload.venue,
        max_participants=payload.max_participants,
        description=payload.description,
        cover_image_url=payload.cover_image_url,
    )
    db.add(event)
    try:
        db.flush()

        event.agendas = [EventAgenda(**agenda.model_dump()) for agenda in payload.agendas]
        event.additional_info = [
            AdditionalEventInfo(**info.model_dump()) for info in payload.additional_info
        ]
        event.mentors = [EventMentor(**mentor.model_dump()) for mentor in payload.mentors]

        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create event",
        ) from exc
    db.refresh(event)
    return event


@router.patch("/events/{event_id}", response_model=PrivateEventResponse)
async def update_event(
    event_id: uuid.UUID,
    request: Request,
    db: DbSession,
    current_user: ClubOrLabAdmin,
) -> Event:
    """Update an event, replacing any supplied child collections wholesale."""
    event = db.scalar(
        select(Event)
        .where(Event.id == event_id)
        .options(
            selectinload(Event.agendas),
            selectinload(Event.additional_info),
            selectinload(Event.mentors),
            selectinload(Event.rejection_reason),
        )
    )
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    content_type = request.headers.get("content-type", "")
    if "multipart/form-data" in content_type:
        form = await request.form()
        name = form.get("name")
        short_description = form.get("short_description")
        category = form.get("category")
        event_date = form.get("event_date")
        registration_deadline = form.get("registration_deadline")
        venue = form.get("venue")
        max_participants = form.get("max_participants")
        description = form.get("description")
        cover_image_url = form.get("cover_image_url")
        status_val = form.get("status")

        # Parse child collections
        agendas_raw = form.get("agendas")
        try:
            agendas = json.loads(agendas_raw) if agendas_raw else None
        except Exception:
            agendas = None

        additional_info_raw = form.get("additional_info")
        try:
            additional_info = json.loads(additional_info_raw) if additional_info_raw else None
        except Exception:
            additional_info = None

        mentors_raw = form.get("mentors")
        try:
            mentors = json.loads(mentors_raw) if mentors_raw else None
        except Exception:
            mentors = None

        # Handle image file upload to Cloudinary
        cover_image_file = form.get("cover_image")
        if cover_image_file and hasattr(cover_image_file, "file") and getattr(cover_image_file, "filename", None):
            if settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET:
                try:
                    import cloudinary
                    import cloudinary.uploader

                    cloudinary.config(
                        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                        api_key=settings.CLOUDINARY_API_KEY,
                        api_secret=settings.CLOUDINARY_API_SECRET,
                    )
                    file_bytes = await cover_image_file.read()
                    if file_bytes:
                        upload_result = cloudinary.uploader.upload(
                            file_bytes,
                            folder="club-management/events",
                            resource_type="image",
                        )
                        cover_image_url = upload_result.get("secure_url")
                except Exception:
                    pass

        payload_dict = {}
        if name is not None:
            payload_dict["name"] = name
        if short_description is not None:
            payload_dict["short_description"] = short_description
        if category is not None:
            payload_dict["category"] = category
        if event_date is not None:
            payload_dict["event_date"] = event_date
        if registration_deadline is not None:
            payload_dict["registration_deadline"] = registration_deadline
        if venue is not None:
            payload_dict["venue"] = venue
        if max_participants is not None:
            payload_dict["max_participants"] = int(max_participants)
        if description is not None:
            payload_dict["description"] = description
        if cover_image_url is not None:
            payload_dict["cover_image_url"] = cover_image_url
        if status_val is not None:
            payload_dict["status"] = status_val
        if agendas is not None:
            payload_dict["agendas"] = agendas
        if additional_info is not None:
            payload_dict["additional_info"] = additional_info
        if mentors is not None:
            payload_dict["mentors"] = mentors

        try:
            payload = EventUpdate.model_validate(payload_dict)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc
    else:
        try:
            body = await request.json()
            payload = EventUpdate.model_validate(body)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc

    update_data = payload.model_dump(exclude_unset=True)
    agendas = update_data.pop("agendas", None)
    additional_info = update_data.pop("additional_info", None)
    mentors = update_data.pop("mentors", None)
    rejection_reason = update_data.pop("rejection_reason", None)

    for field, value in update_data.items():
        setattr(event, field, value)

    try:
        if agendas is not None:
            event.agendas = [EventAgenda(**agenda.model_dump()) for agenda in agendas]
        if additional_info is not None:
            event.additional_info = [
                AdditionalEventInfo(**info.model_dump()) for info in additional_info
            ]
        if mentors is not None:
            event.mentors = [EventMentor(**mentor.model_dump()) for mentor in mentors]
        if rejection_reason is not None:
            event.status = EventStatus.REJECTED
            if event.rejection_reason is None:
                event.rejection_reason = EventRejectReason(
                    event_id=event.id,
                    **rejection_reason,
                )
            else:
                for k, v in rejection_reason.items():
                    setattr(event.rejection_reason, k, v)
        elif event.status == EventStatus.PENDING and event.rejection_reason is not None:
            # Resubmitted event clears previous rejection reason
            db.delete(event.rejection_reason)
            event.rejection_reason = None

        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update event",
        ) from exc
    db.refresh(event)
    return event


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: uuid.UUID,
    db: DbSession,
    current_user: ClubOrLabAdmin,
) -> None:
    """Delete an event and all its cascaded associations."""
    event = db.scalar(select(Event).where(Event.id == event_id))
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    db.delete(event)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete event",
        ) from exc


@router.get("/events/private", response_model=list[PrivateEventResponse])
def list_private_events(db: DbSession, current_user: CurrentUser) -> list[Event]:
    """Fetch all events with their child collections for authenticated users."""
    stmt = (
        select(Event)
        .options(
            selectinload(Event.agendas),
            selectinload(Event.additional_info),
            selectinload(Event.mentors),
            selectinload(Event.rejection_reason),
        )
        .order_by(Event.event_date.asc())
    )
    if current_user.role == UserRole.STUDENT:
        stmt = stmt.where(Event.status != EventStatus.REJECTED)
    return list(db.scalars(stmt).all())


@router.get("/events", response_model=list[EventResponse])
def list_public_events(db: DbSession) -> list[EventResponse]:
    """Fetch all active public events."""
    stmt = (
        select(Event)
        .where(Event.status != EventStatus.REJECTED)
        .options(selectinload(Event.winners))
        .order_by(Event.event_date.asc())
    )
    events = db.scalars(stmt).all()
    return [_public_event_response(e) for e in events]


@router.get("/events/{event_id}", response_model=EventResponse)
def get_public_event(event_id: uuid.UUID, db: DbSession) -> EventResponse:
    """Fetch the public event details, exposing only non-private fields."""
    event = db.scalar(
        select(Event).where(Event.id == event_id).options(selectinload(Event.winners))
    )
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return _public_event_response(event)


@router.get("/events/{event_id}/private", response_model=PrivateEventResponse)
def get_private_event(event_id: uuid.UUID, db: DbSession, current_user: CurrentUser) -> Event:
    """Fetch the full event with its child collections."""
    event = db.scalar(
        select(Event)
        .where(Event.id == event_id)
        .options(
            selectinload(Event.agendas),
            selectinload(Event.additional_info),
            selectinload(Event.mentors),
            selectinload(Event.rejection_reason),
        )
    )
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    return event


# ----------------------------------------------------------- Registrations
@router.post(
    "/events/registrations",
    response_model=EventRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event_registration(
    payload: EventRegistrationCreate,
    db: DbSession,
    current_user: StudentOnly,
) -> EventRegistrationResponse:
    """Register a student for an event from the profile submitted by the frontend.

    Only the user account exists beforehand; the ``Student`` record is created
    here from the submitted form data on first registration. If the current user
    already has a student profile, only their skill domains are extended with
    any new technologies; the rest of their details are left untouched. The
    ``student_id``
    (college ID string) is stored on the Student and the Student UUID is
    referenced by the registration. Registration and attendance statuses come
    from the model defaults.
    """
    event = db.scalar(select(Event).where(Event.id == payload.event_id))
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    student = db.scalar(select(Student).where(Student.user_id == current_user.id))
    if student is None:
        student = Student(
            user_id=current_user.id,
            student_id=payload.student_id,
            department=Department(payload.department),
            phone=payload.phone,
            github_url=payload.github,
            linkedin_url=payload.linkedin,
            portfolio_url=payload.portfolio,
        )
        db.add(student)
        db.flush()
        current_user.full_name = payload.name
        current_user.email = payload.email
    _sync_student_domains(db, student, payload.domains)

    existing = db.scalar(
        select(EventRegistration).where(
            EventRegistration.event_id == payload.event_id,
            EventRegistration.student_id == student.id,
        )
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already registered for this event",
        )

    registration_id = uuid.uuid4()
    qr_code_url = generate_registration_qr_code(
        registration_id=registration_id,
        event_id=payload.event_id,
        student_id=student.id,
        api_prefix=settings.API_STR,
    )

    registration = EventRegistration(
        id=registration_id,
        event_id=payload.event_id,
        student_id=student.id,
        team_name=payload.team_name,
        qr_code_url=qr_code_url,
    )
    db.add(registration)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create registration",
        ) from exc
    db.refresh(registration)
    return _registration_response(registration)


@router.get(
    "/events/registrations/me",
    response_model=list[EventRegistrationResponse],
)
def get_my_event_registrations(
    db: DbSession,
    current_user: StudentOnly,
) -> list[EventRegistrationResponse]:
    """Fetch all event registrations and passes belonging to the authenticated student."""
    student = _get_current_student(db, current_user)

    stmt = (
        select(EventRegistration)
        .where(EventRegistration.student_id == student.id)
        .options(*_registration_eager_loads())
        .order_by(EventRegistration.id.desc())
    )
    registrations = db.scalars(stmt).all()
    return [_registration_response(r) for r in registrations]


@router.post(
    "/events/registrations/verify",
    response_model=RegistrationVerifyResponse,
)
def verify_event_registration_pass(
    payload: RegistrationVerifyRequest,
    db: DbSession,
    current_user: ClubOrLabAdmin,
) -> RegistrationVerifyResponse:
    """Verify an event pass via scanned QR code data or registration ID and mark attendance.
    
    Accessible by Lab Administrators and Club Administrators.
    """
    target_uuid, short_prefix = extract_registration_identifier(
        payload.qr_data or (str(payload.registration_id) if payload.registration_id else "")
    )

    registration = None
    if target_uuid is not None:
        registration = db.scalar(
            select(EventRegistration)
            .where(EventRegistration.id == target_uuid)
            .options(*_registration_eager_loads())
        )
        if registration is None:
            registration = db.scalar(
                select(EventRegistration)
                .where(EventRegistration.event_id == target_uuid)
                .options(*_registration_eager_loads())
                .order_by(EventRegistration.id.desc())
            )
    elif short_prefix:
        registration = db.scalar(
            select(EventRegistration)
            .where(cast(EventRegistration.id, String).ilike(f"{short_prefix}%"))
            .options(*_registration_eager_loads())
        )
        if registration is None:
            registration = db.scalar(
                select(EventRegistration)
                .where(cast(EventRegistration.event_id, String).ilike(f"{short_prefix}%"))
                .options(*_registration_eager_loads())
                .order_by(EventRegistration.id.desc())
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid QR code data or registration ID format",
        )

    already_marked = registration.attendance_status == AttendanceStatus.PRESENT
    event_date = registration.event.event_date
    today_utc = datetime.now(UTC).date()
    today_local = datetime.now().date()

    # Strict Event Date Verification: Scanning is only open on event day
    if event_date > today_local and event_date > today_utc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Scanning is not open yet. Event '{registration.event.name}' is scheduled for {event_date.strftime('%d %b %Y')}.",
        )
    if event_date < today_local and event_date < today_utc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Event '{registration.event.name}' has already concluded (Date: {event_date.strftime('%d %b %Y')}).",
        )

    if not already_marked:
        registration.attendance_status = AttendanceStatus.PRESENT
        try:
            db.commit()
        except Exception as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update attendance status",
            ) from exc
        db.refresh(registration)
        msg = f"Attendance marked as Present for {registration.student.user.full_name}."
    else:
        msg = f"Student {registration.student.user.full_name} is already marked Present."

    return RegistrationVerifyResponse(
        success=True,
        message=msg,
        already_marked=already_marked,
        scanned_at=datetime.now(UTC),
        registration=_registration_response(registration),
    )


@router.post(
    "/events/registrations/{registration_id}/verify",
    response_model=RegistrationVerifyResponse,
)
def verify_event_registration_by_id(
    registration_id: uuid.UUID,
    db: DbSession,
    current_user: ClubOrLabAdmin,
) -> RegistrationVerifyResponse:
    """Verify an event pass by registration ID and mark attendance as Present."""
    registration = db.scalar(
        select(EventRegistration)
        .where(EventRegistration.id == registration_id)
        .options(*_registration_eager_loads())
    )
    if registration is None:
        registration = db.scalar(
            select(EventRegistration)
            .where(EventRegistration.event_id == registration_id)
            .options(*_registration_eager_loads())
            .order_by(EventRegistration.id.desc())
        )
    if registration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event registration pass not found",
        )

    already_marked = registration.attendance_status == AttendanceStatus.PRESENT
    event_date = registration.event.event_date
    today_utc = datetime.now(UTC).date()
    today_local = datetime.now().date()

    # Strict Event Date Verification: Scanning is only open on event day
    if event_date > today_local and event_date > today_utc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Scanning is not open yet. Event '{registration.event.name}' is scheduled for {event_date.strftime('%d %b %Y')}.",
        )
    if event_date < today_local and event_date < today_utc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Event '{registration.event.name}' has already concluded (Date: {event_date.strftime('%d %b %Y')}).",
        )

    if not already_marked:
        registration.attendance_status = AttendanceStatus.PRESENT
        try:
            db.commit()
        except Exception as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update attendance status",
            ) from exc
        db.refresh(registration)
        msg = f"Attendance marked as Present for {registration.student.user.full_name}."
    else:
        msg = f"Student {registration.student.user.full_name} is already marked Present."

    return RegistrationVerifyResponse(
        success=True,
        message=msg,
        already_marked=already_marked,
        scanned_at=datetime.now(UTC),
        registration=_registration_response(registration),
    )


@router.patch(
    "/events/registrations/{registration_id}",
    response_model=EventRegistrationResponse,
)
def update_event_registration(
    registration_id: uuid.UUID,
    payload: EventRegistrationUpdate,
    db: DbSession,
    current_user: StudentOnly,
) -> EventRegistrationResponse:
    """Update the student's own registration.

    Only ``team_name`` and the editable student profile fields (``github``,
    ``linkedin``, ``portfolio``, ``domains``) are accepted. Protected fields
    (``event_id``, ``student_id``, ``registration_status``, ``attendance_status``)
    are rejected at the schema level via ``extra="forbid"`` (422).
    """
    student = _get_current_student(db, current_user)

    registration = db.scalar(
        select(EventRegistration)
        .where(EventRegistration.id == registration_id)
        .options(*_registration_eager_loads())
    )
    if registration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found",
        )
    if registration.student_id != student.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to modify this registration",
        )

    update_data = payload.model_dump(exclude_unset=True)
    reg_student = registration.student

    if "team_name" in update_data:
        registration.team_name = update_data["team_name"]
    if "github" in update_data:
        reg_student.github_url = update_data["github"]
    if "linkedin" in update_data:
        reg_student.linkedin_url = update_data["linkedin"]
    if "portfolio" in update_data:
        reg_student.portfolio_url = update_data["portfolio"]
    if payload.domains is not None:
        _sync_student_domains(db, reg_student, payload.domains)

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update registration",
        ) from exc
    db.refresh(registration)
    return _registration_response(registration)


@router.get(
    "/events/registrations/{registration_id}",
    response_model=EventRegistrationResponse,
)
def get_event_registration(
    registration_id: uuid.UUID,
    db: DbSession,
    current_user: StudentOnly,
) -> EventRegistrationResponse:
    """Fetch the student's own registration, including submitted student info."""
    student = _get_current_student(db, current_user)

    registration = db.scalar(
        select(EventRegistration)
        .where(EventRegistration.id == registration_id)
        .options(*_registration_eager_loads())
    )
    if registration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found",
        )
    if registration.student_id != student.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to view this registration",
        )
    return _registration_response(registration)


# --------------------------------------------------------------- Winners
@router.post(
    "/events/winners",
    response_model=EventWinnerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event_winner(
    payload: EventWinnerCreate,
    db: DbSession,
    current_user: ClubAdmin,
) -> EventWinner:
    """Declare a winner for an event (club admin only).

    Verifies the event and registration exist, that the registration belongs to
    the event, and that neither the registration nor the position is already
    taken for that event.
    """
    event = db.scalar(select(Event).where(Event.id == payload.event_id))
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    registration = db.scalar(
        select(EventRegistration).where(EventRegistration.id == payload.registration_id)
    )
    if registration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found",
        )
    if registration.event_id != payload.event_id:   
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Registration does not belong to this event",
        )

    if (
        db.scalar(
            select(EventWinner).where(EventWinner.registration_id == payload.registration_id)
        )
        is not None
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Registration is already a winner",
        )

    if (
        db.scalar(
            select(EventWinner).where(
                EventWinner.event_id == payload.event_id,
                EventWinner.position == payload.position,
            )
        )
        is not None
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Position already occupied for this event",
        )

    winner = EventWinner(
        event_id=payload.event_id,
        registration_id=payload.registration_id,
        position=payload.position,
        project_name=payload.project_name,
        project_url=payload.project_url,
    )
    db.add(winner)
    try:
        db.commit()
    except IntegrityError as exc:
        # Race: unique constraint on (registration) or (event, position).
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Winner already exists for this registration or position",
        ) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create winner",
        ) from exc
    db.refresh(winner)
    return winner


@router.put(
    "/events/winners",
    response_model=list[EventWinnerResponse],
)
def upsert_event_winners(
    payload: list[EventWinnerCreate],
    db: DbSession,
    current_user: ClubAdmin,
) -> list[EventWinner]:
    """Update all winner positions for an event from the payload (club admin only).

    Each item carries an ``event_id`` and ``position``. The winner for that
    (event, position) is created if missing or updated otherwise, keyed on the
    registration and project details. Positions not present in the payload are
    left untouched.
    """
    for event_id in {item.event_id for item in payload}:
        if db.scalar(select(Event).where(Event.id == event_id)) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

    results: list[EventWinner] = []
    for item in payload:
        registration = db.scalar(
            select(EventRegistration).where(
                EventRegistration.id == item.registration_id,
                EventRegistration.event_id == item.event_id,
            )
        )
        if registration is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registration not found for this event",
            )

        winner = db.scalar(
            select(EventWinner).where(
                EventWinner.event_id == item.event_id,
                EventWinner.position == item.position,
            )
        )
        if winner is None:
            winner = EventWinner(
                event_id=item.event_id,
                registration_id=item.registration_id,
                position=item.position,
                project_name=item.project_name,
                project_url=item.project_url,
            )
            db.add(winner)
        else:
            winner.registration_id = item.registration_id
            winner.project_name = item.project_name
            winner.project_url = item.project_url
        results.append(winner)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflict while updating winners",
        ) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update winners",
        ) from exc
    for winner in results:
        db.refresh(winner)
    return results


@router.get("/events/{event_id}/winners", response_model=list[EventWinnerResponse])
def get_event_winners(event_id: uuid.UUID, db: DbSession) -> list[EventWinner]:
    """Fetch all winners (all positions) for an event (no authentication
    required)."""
    event = db.scalar(select(Event).where(Event.id == event_id))
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    return list(
        db.scalars(
            select(EventWinner)
            .where(EventWinner.event_id == event_id)
            .order_by(EventWinner.position)
        )
    )


# ---------------------------------------------------------- Certificate
@router.post(
    "/events/{event_id}/certificates",
    response_model=list[CertificateResponse],
    status_code=status.HTTP_201_CREATED,
)
def generate_event_certificates(
    event_id: uuid.UUID,
    db: DbSession,
    current_user: ClubAdmin,
) -> list[CertificateResponse]:
    """Generate a certificate for every registration of an event (club admin
    only).

    Registrations that already have a certificate are skipped, so repeated
    calls never create duplicates. Winner registrations receive the certificate
    matching their position; everyone else receives a participation
    certificate. ``issue_date`` is today's date and ``certificate_url`` is
    left ``NULL`` until a later service generates the PDF.
    """
    event = db.scalar(select(Event).where(Event.id == event_id))
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    registrations = list(
        db.scalars(
            select(EventRegistration)
            .where(EventRegistration.event_id == event_id)
            .options(selectinload(EventRegistration.winner))
        )
    )
    if not registrations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No registrations found for this event",
        )

    certificates: list[Certificate] = []
    for registration in registrations:
        existing = db.scalar(
            select(Certificate).where(Certificate.registration_id == registration.id)
        )
        if existing is not None:
            continue

        certificate_type = CertificateType.PARTICIPATION
        if registration.winner is not None:
            certificate_type = _CERTIFICATE_TYPE_BY_POSITION[registration.winner.position]

        certificate = Certificate(
            event_id=event_id,
            student_id=registration.student_id,
            registration_id=registration.id,
            certificate_type=certificate_type,
            issue_date=datetime.now(UTC).date(),
        )
        db.add(certificate)
        certificates.append(certificate)

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate certificates",
        ) from exc
    for certificate in certificates:
        db.refresh(certificate)
    return [_certificate_response(certificate) for certificate in certificates]


@router.get(
    "/students/{student_id}/certificates",
    response_model=list[CertificateResponse],
)
def get_student_certificates(
    student_id: uuid.UUID,
    db: DbSession,
    current_user: StudentOnly,
) -> list[CertificateResponse]:
    """Fetch every certificate belonging to a student (student only).

    ``student_id`` is the Student UUID. Certificates are ordered by issue date.
    """
    student = db.scalar(select(Student).where(Student.id == student_id))
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    certificates = list(
        db.scalars(
            select(Certificate)
            .where(Certificate.student_id == student_id)
            .order_by(Certificate.issue_date)
        )
    )
    return [_certificate_response(certificate) for certificate in certificates]