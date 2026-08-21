"""Integration tests for the event endpoints.

Each test is self-contained and creates its own data via the API or the
``db_session`` fixture, never relying on test execution order.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.event import Event, EventRegistration, EventWinner
from app.models.student import Student
from app.models.user import User
from app.utils.enums import Department, UserRole, WinnerPosition
from tests.conftest import auth_headers

API = "/api/events"


def _valid_event_payload(**overrides: object) -> dict:
    """A minimal valid payload for creating an event."""
    payload: dict = {
        "name": "Intro to AI Workshop",
        "short_description": "A hands-on introduction to AI",
        "category": "workshop",
        "event_date": "2026-10-15",
        "registration_deadline": "2026-10-10T12:00:00Z",
        "venue": "seminar_hall",
        "max_participants": 40,
        "description": "Full-day workshop covering AI fundamentals.",
        "agendas": "[]",
        "additional_info": "[]",
        "mentors": "[]",
    }
    payload.update(overrides)
    return payload


def _create_event_in_db(db: Session, name: str = "Existing Event") -> Event:
    """Insert an event row directly, bypassing the API."""
    event = Event(
        name=name,
        short_description="Already exists",
        category="workshop",
        event_date=date(2026, 11, 1),
        registration_deadline=datetime(2026, 10, 20, tzinfo=UTC),
        venue="auditorium",
        max_participants=30,
        description="Pre-seeded event for read tests.",
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def _create_student_user(db: Session, *, email: str) -> User:
    """Insert a student user. The linked Student profile is created at
    registration time by the endpoint."""
    user = User(
        full_name="Stu",
        email=email,
        password_hash=get_password_hash("testpassword123"),
        role=UserRole.STUDENT,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _create_admin(db: Session, *, email: str) -> User:
    """Insert a club admin user."""
    user = User(
        full_name="Admin",
        email=email,
        password_hash=get_password_hash("testpassword123"),
        role=UserRole.CLUB_ADMIN,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _create_registration_in_db(
    db: Session, *, event: Event, email: str, college_id: str
) -> EventRegistration:
    """Insert a student user, its Student profile and an event registration."""
    user = _create_student_user(db, email=email)
    student = Student(
        user_id=user.id,
        student_id=college_id,
        department=Department.COMPUTER_SCIENCE,
    )
    db.add(student)
    db.flush()
    registration = EventRegistration(
        event_id=event.id, student_id=student.id, team_name="Team"
    )
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return registration


def _registration_payload(
    event_id: str, college_id: str, *, email: str | None = None, **overrides: object
) -> dict:
    """A minimal valid registration form payload."""
    payload: dict = {
        "name": "Stu",
        "student_id": college_id,
        "email": email or f"{college_id.lower()}@example.com",
        "phone": "12345",
        "department": "computer_science",
        "github": "gh",
        "linkedin": "li",
        "portfolio": "pf",
        "event_id": event_id,
        "team_name": "Alpha",
        "domains": [
            {
                "domain": "WEB_DEVELOPMENT",
                "technologies": [{"technology": "REACT"}],
            }
        ],
    }
    payload.update(overrides)
    return payload


# ---------------------------------------------------------------- POST /events
def test_create_event_as_club_admin(
    client: TestClient, club_admin: User, db_session: Session
) -> None:
    """1. Event creation WITHOUT a cover image succeeds, cover_image_url is None."""
    response = client.post(
        f"{API}",
        data=_valid_event_payload(),
        headers=auth_headers(club_admin),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Intro to AI Workshop"
    assert body["status"] == "pending"
    assert body["cover_image_url"] is None

    # Verify persisted in database with null cover_image_url
    event = db_session.scalar(select(Event).where(Event.id == uuid.UUID(body["id"])))
    assert event is not None
    assert event.cover_image_url is None


def test_create_event_with_valid_jpeg_image_success(
    client: TestClient, club_admin: User, db_session: Session, monkeypatch
) -> None:
    """2. Event creation WITH a valid JPEG image uploads to Cloudinary and saves secure_url."""
    mock_url = "https://res.cloudinary.com/test-cloud/image/upload/v12345/club-management/events/event_cover.jpg"
    upload_called = False

    async def fake_upload(file, folder="club-management/events"):
        nonlocal upload_called
        upload_called = True
        assert folder == "club-management/events"
        return mock_url

    monkeypatch.setattr("app.api.routes.event.upload_image_to_cloudinary", fake_upload)

    payload = _valid_event_payload(name="JPEG Workshop")
    files = {"cover_image": ("cover.jpg", b"\xff\xd8\xff\xe0fake_jpeg_content", "image/jpeg")}

    response = client.post(
        f"{API}",
        data=payload,
        files=files,
        headers=auth_headers(club_admin),
    )

    assert response.status_code == 201
    assert upload_called is True
    body = response.json()
    assert body["cover_image_url"] == mock_url

    # Verify persisted in database
    event = db_session.scalar(select(Event).where(Event.id == uuid.UUID(body["id"])))
    assert event is not None
    assert event.cover_image_url == mock_url


def test_create_event_with_valid_png_image_success(
    client: TestClient, club_admin: User, db_session: Session, monkeypatch
) -> None:
    """3. Event creation WITH a valid PNG image uploads to Cloudinary and saves secure_url."""
    mock_url = "https://res.cloudinary.com/test-cloud/image/upload/v12345/club-management/events/event_cover.png"

    async def fake_upload(file, folder="club-management/events"):
        return mock_url

    monkeypatch.setattr("app.api.routes.event.upload_image_to_cloudinary", fake_upload)

    payload = _valid_event_payload(name="PNG Workshop")
    files = {"cover_image": ("banner.png", b"\x89PNG\r\n\x1a\nfake_png_data", "image/png")}

    response = client.post(
        f"{API}",
        data=payload,
        files=files,
        headers=auth_headers(club_admin),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["cover_image_url"] == mock_url


def test_create_event_with_valid_webp_image_success(
    client: TestClient, club_admin: User, db_session: Session, monkeypatch
) -> None:
    """4. Event creation WITH a valid WebP image uploads to Cloudinary and saves secure_url."""
    mock_url = "https://res.cloudinary.com/test-cloud/image/upload/v12345/club-management/events/event_cover.webp"

    async def fake_upload(file, folder="club-management/events"):
        return mock_url

    monkeypatch.setattr("app.api.routes.event.upload_image_to_cloudinary", fake_upload)

    payload = _valid_event_payload(name="WebP Workshop")
    files = {"cover_image": ("banner.webp", b"RIFF....WEBPfake_webp_data", "image/webp")}

    response = client.post(
        f"{API}",
        data=payload,
        files=files,
        headers=auth_headers(club_admin),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["cover_image_url"] == mock_url


def test_create_event_invalid_image_type_rejected(
    client: TestClient, club_admin: User, db_session: Session
) -> None:
    """5. Unsupported image type (e.g. image/gif) is rejected with 400 and event is not saved."""
    payload = _valid_event_payload(name="Invalid Type Event")
    files = {"cover_image": ("animation.gif", b"GIF89afake_gif_data", "image/gif")}

    response = client.post(
        f"{API}",
        data=payload,
        files=files,
        headers=auth_headers(club_admin),
    )

    assert response.status_code == 400
    assert "Unsupported image type" in response.json()["detail"]

    # Verify event was NOT created
    event = db_session.scalar(select(Event).where(Event.name == "Invalid Type Event"))
    assert event is None


def test_create_event_image_exceeds_5mb_rejected(
    client: TestClient, club_admin: User, db_session: Session
) -> None:
    """6. Image larger than 5 MB is rejected with 400 and event is not saved."""
    payload = _valid_event_payload(name="Huge Image Event")
    large_content = b"0" * (5 * 1024 * 1024 + 1)
    files = {"cover_image": ("huge.jpg", large_content, "image/jpeg")}

    response = client.post(
        f"{API}",
        data=payload,
        files=files,
        headers=auth_headers(club_admin),
    )

    assert response.status_code == 400
    assert "exceeds maximum limit" in response.json()["detail"]

    # Verify event was NOT created
    event = db_session.scalar(select(Event).where(Event.name == "Huge Image Event"))
    assert event is None


def test_create_event_cloudinary_failure_rollback(
    client: TestClient, club_admin: User, db_session: Session, monkeypatch
) -> None:
    """7 & 8. Cloudinary failure returns 500 and ensures upload happens before DB write."""
    from fastapi import HTTPException

    async def failing_upload(file, folder="club-management/events"):
        raise HTTPException(
            status_code=500,
            detail="Failed to upload image to Cloudinary: Network timeout",
        )

    monkeypatch.setattr("app.api.routes.event.upload_image_to_cloudinary", failing_upload)

    payload = _valid_event_payload(name="Failing Cloudinary Event")
    files = {"cover_image": ("cover.jpg", b"fake_jpeg", "image/jpeg")}

    response = client.post(
        f"{API}",
        data=payload,
        files=files,
        headers=auth_headers(club_admin),
    )

    assert response.status_code == 500
    assert "Failed to upload image to Cloudinary" in response.json()["detail"]

    # Verify event was NOT created/persisted in database
    event = db_session.scalar(select(Event).where(Event.name == "Failing Cloudinary Event"))
    assert event is None


def test_create_event_stored_url_is_not_base64_or_local(
    client: TestClient, club_admin: User, db_session: Session, monkeypatch
) -> None:
    """9. Confirm stored cover_image_url is the Cloudinary secure_url and never Base64 or local file path."""
    cloudinary_url = "https://res.cloudinary.com/demo/image/upload/v12345/events/test.jpg"

    async def fake_upload(file, folder="club-management/events"):
        return cloudinary_url

    monkeypatch.setattr("app.api.routes.event.upload_image_to_cloudinary", fake_upload)

    payload = _valid_event_payload(name="Clean URL Event")
    files = {"cover_image": ("test.jpg", b"jpeg_content", "image/jpeg")}

    response = client.post(
        f"{API}",
        data=payload,
        files=files,
        headers=auth_headers(club_admin),
    )

    assert response.status_code == 201
    event = db_session.scalar(select(Event).where(Event.name == "Clean URL Event"))
    assert event is not None
    assert event.cover_image_url == cloudinary_url
    assert not event.cover_image_url.startswith("data:image/")
    assert not event.cover_image_url.startswith("blob:")
    assert not event.cover_image_url.startswith("file://")
    assert not event.cover_image_url.startswith("C:")


def test_create_event_as_student_forbidden(client: TestClient, student: User) -> None:
    response = client.post(
        f"{API}",
        data=_valid_event_payload(),
        headers=auth_headers(student),
    )

    assert response.status_code == 403


def test_create_event_invalid_payload(client: TestClient, club_admin: User) -> None:
    response = client.post(
        f"{API}",
        data=_valid_event_payload(max_participants=0),
        headers=auth_headers(club_admin),
    )

    assert response.status_code == 422


def test_create_event_missing_required_field(
    client: TestClient, club_admin: User
) -> None:
    payload = _valid_event_payload()
    del payload["description"]

    response = client.post(f"{API}", data=payload, headers=auth_headers(club_admin))

    assert response.status_code == 422


def test_create_event_unauthenticated(client: TestClient) -> None:
    response = client.post(f"{API}", data=_valid_event_payload())

    assert response.status_code == 401


# ------------------------------------------------------- GET /events/{event_id}
def test_get_event_success(client: TestClient, db_session: Session) -> None:
    event = _create_event_in_db(db_session)

    response = client.get(f"{API}/{event.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(event.id)
    assert body["name"] == event.name


def test_get_event_invalid_uuid(client: TestClient) -> None:
    response = client.get(f"{API}/not-a-uuid")

    assert response.status_code == 422


def test_get_event_not_found(client: TestClient) -> None:
    response = client.get(f"{API}/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404


def test_get_event_response_body(client: TestClient, db_session: Session) -> None:
    event = _create_event_in_db(db_session, name="Robotics Hackathon")

    response = client.get(f"{API}/{event.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Robotics Hackathon"
    assert body["short_description"] == "Already exists"
    assert body["category"] == "workshop"
    assert body["event_date"] == "2026-11-01"
    assert body["venue"] == "auditorium"
    assert body["max_participants"] == 30
    assert body["description"] == "Pre-seeded event for read tests."


def test_get_event_winner_fields_null_when_no_winners(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session)

    response = client.get(f"{API}/{event.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["winner_name"] is None
    assert body["winner_project_url"] is None


def test_get_event_does_not_expose_private_fields(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session)

    response = client.get(f"{API}/{event.id}")

    assert response.status_code == 200
    body = response.json()
    assert "registration_deadline" not in body
    assert "status" not in body
    assert "created_at" not in body
    assert "updated_at" not in body


# ----------------------------------------------------- POST /events/registrations
def test_create_registration_uses_submitted_student_profile(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session)
    user = _create_student_user(db_session, email="reg1@example.com")

    response = client.post(
        f"{API}/registrations",
        json=_registration_payload(str(event.id), "CS0001"),
        headers=auth_headers(user),
    )

    assert response.status_code == 201
    body = response.json()
    student = db_session.scalar(select(Student).where(Student.user_id == user.id))
    assert student is not None
    assert body["event_id"] == str(event.id)
    assert body["student_id"] == str(student.id)
    assert body["team_name"] == "Alpha"
    assert body["registration_status"] == "pending"
    assert body["attendance_status"] == "absent"
    assert body["student"]["student_id"] == "CS0001"
    assert body["student"]["name"] == "Stu"
    assert body["student"]["email"] == "cs0001@example.com"
    assert body["student"]["domains"] == [
        {
            "domain": "WEB_DEVELOPMENT",
            "technologies": [{"technology": "REACT"}],
        }
    ]
    assert body["event"]["id"] == str(event.id)
    assert body["event"]["name"] == event.name
    assert body["event"]["short_description"] == event.short_description
    assert body["event"]["event_date"] == "2026-11-01"
    assert body["event"]["venue"] == "auditorium"
    assert body["event"]["winner_name"] is None
    assert body["event"]["winner_project_url"] is None
    assert "status" not in body["event"]


def test_create_registration_syncs_profile_to_student(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session)
    user = _create_student_user(db_session, email="reg2@example.com")

    response = client.post(
        f"{API}/registrations",
        json=_registration_payload(str(event.id), "CS0002"),
        headers=auth_headers(user),
    )

    assert response.status_code == 201
    db_session.refresh(user)
    student = db_session.scalar(select(Student).where(Student.user_id == user.id))
    assert student is not None
    assert student.student_id == "CS0002"
    assert student.department == Department.COMPUTER_SCIENCE
    assert student.phone == "12345"
    assert student.github_url == "gh"
    assert student.linkedin_url == "li"
    assert student.portfolio_url == "pf"
    assert [sd.domain.name.value for sd in student.domains] == ["WEB_DEVELOPMENT"]
    assert user.full_name == "Stu"
    assert user.email == "cs0002@example.com"


def test_create_registration_creates_student_for_user(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session)
    user = _create_student_user(db_session, email="reg3@example.com")

    response = client.post(
        f"{API}/registrations",
        json=_registration_payload(str(event.id), "CS0003"),
        headers=auth_headers(user),
    )

    assert response.status_code == 201
    student = db_session.scalar(select(Student).where(Student.user_id == user.id))
    assert student is not None
    assert student.student_id == "CS0003"


def test_create_registration_event_not_found(
    client: TestClient, db_session: Session
) -> None:
    user = _create_student_user(db_session, email="reg4@example.com")

    response = client.post(
        f"{API}/registrations",
        json=_registration_payload("00000000-0000-0000-0000-000000000000", "CS0004"),
        headers=auth_headers(user),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_registration_keeps_existing_details_and_appends_domains(
    client: TestClient, db_session: Session
) -> None:
    event_a = _create_event_in_db(db_session, name="Event A")
    event_b = _create_event_in_db(db_session, name="Event B")
    user = _create_student_user(db_session, email="reg4b@example.com")

    first = client.post(
        f"{API}/registrations",
        json=_registration_payload(
            str(event_a.id),
            "CS0016",
            email="kept@example.com",
            phone="111",
            github="orig",
            domains=[
                {
                    "domain": "WEB_DEVELOPMENT",
                    "technologies": [{"technology": "REACT"}],
                }
            ],
        ),
        headers=auth_headers(user),
    )
    assert first.status_code == 201

    second = client.post(
        f"{API}/registrations",
        json=_registration_payload(
            str(event_b.id),
            "CS9999",
            email="changed@example.com",
            phone="222",
            github="hacker",
            domains=[
                {
                    "domain": "WEB_DEVELOPMENT",
                    "technologies": [{"technology": "REACT"}],
                },
                {
                    "domain": "BACKEND_DEVELOPMENT",
                    "technologies": [{"technology": "FASTAPI"}],
                },
            ],
        ),
        headers=auth_headers(user),
    )
    assert second.status_code == 201

    db_session.refresh(user)
    student = db_session.scalar(select(Student).where(Student.user_id == user.id))
    assert student is not None
    assert student.student_id == "CS0016"
    assert student.phone == "111"
    assert student.github_url == "orig"
    assert student.department == Department.COMPUTER_SCIENCE
    assert user.email == "kept@example.com"
    assert sorted(sd.domain.name.value for sd in student.domains) == [
        "BACKEND_DEVELOPMENT",
        "WEB_DEVELOPMENT",
    ]


def test_create_registration_duplicate_conflict(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session)
    user = _create_student_user(db_session, email="reg5@example.com")
    payload = _registration_payload(str(event.id), "CS0005")

    first = client.post(
        f"{API}/registrations", json=payload, headers=auth_headers(user)
    )
    second = client.post(
        f"{API}/registrations", json=payload, headers=auth_headers(user)
    )

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["detail"] == "Already registered for this event"


def test_create_registration_invalid_department(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session)
    user = _create_student_user(db_session, email="reg6@example.com")

    response = client.post(
        f"{API}/registrations",
        json=_registration_payload(str(event.id), "CS0006", department="not-a-department"),
        headers=auth_headers(user),
    )

    assert response.status_code == 422


def test_create_registration_rejects_unexpected_field(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session)
    user = _create_student_user(db_session, email="reg6b@example.com")
    payload = _registration_payload(str(event.id), "CS0006B")
    payload["unexpected"] = "value"

    response = client.post(
        f"{API}/registrations", json=payload, headers=auth_headers(user)
    )

    assert response.status_code == 422


def test_create_registration_as_club_admin_forbidden(
    client: TestClient, db_session: Session, club_admin: User
) -> None:
    event = _create_event_in_db(db_session)
    _create_student_user(db_session, email="reg7@example.com")

    response = client.post(
        f"{API}/registrations",
        json=_registration_payload(str(event.id), "CS0007"),
        headers=auth_headers(club_admin),
    )

    assert response.status_code == 403


# ----------------------------------------- PATCH /events/registrations/{id}
def test_update_registration_updates_editable_fields(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session)
    user = _create_student_user(db_session, email="reg8@example.com")
    created = client.post(
        f"{API}/registrations",
        json=_registration_payload(str(event.id), "CS0008"),
        headers=auth_headers(user),
    )
    reg_id = created.json()["id"]

    response = client.patch(
        f"{API}/registrations/{reg_id}",
        json={
            "team_name": "Team B",
            "github": "gh2",
            "domains": [
                {
                    "domain": "AI_ML",
                    "technologies": [{"technology": "PYTORCH"}],
                }
            ],
        },
        headers=auth_headers(user),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["team_name"] == "Team B"
    assert body["student"]["github"] == "gh2"
    assert body["student"]["domains"] == [
        {
            "domain": "WEB_DEVELOPMENT",
            "technologies": [{"technology": "REACT"}],
        },
        {
            "domain": "AI_ML",
            "technologies": [{"technology": "PYTORCH"}],
        },
    ]


def test_update_registration_rejects_protected_fields(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session)
    user = _create_student_user(db_session, email="reg9@example.com")
    created = client.post(
        f"{API}/registrations",
        json=_registration_payload(str(event.id), "CS0009"),
        headers=auth_headers(user),
    )
    reg_id = created.json()["id"]

    response = client.patch(
        f"{API}/registrations/{reg_id}",
        json={"registration_status": "registered"},
        headers=auth_headers(user),
    )

    assert response.status_code == 422


def test_update_other_students_registration_forbidden(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session)
    owner = _create_student_user(db_session, email="reg10@example.com")
    other = _create_student_user(db_session, email="reg11@example.com")
    other_event = _create_event_in_db(db_session, name="Other Event")
    client.post(
        f"{API}/registrations",
        json=_registration_payload(
            str(other_event.id), "CS0011", email="other@example.com"
        ),
        headers=auth_headers(other),
    )
    created = client.post(
        f"{API}/registrations",
        json=_registration_payload(str(event.id), "CS0010"),
        headers=auth_headers(owner),
    )
    reg_id = created.json()["id"]

    response = client.patch(
        f"{API}/registrations/{reg_id}",
        json={"team_name": "Nope"},
        headers=auth_headers(other),
    )

    assert response.status_code == 403


# ------------------------------------------ GET /events/registrations/{id}
def test_get_registration_returns_embedded_student_profile(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session)
    user = _create_student_user(db_session, email="reg12@example.com")
    created = client.post(
        f"{API}/registrations",
        json=_registration_payload(str(event.id), "CS0012"),
        headers=auth_headers(user),
    )
    reg_id = created.json()["id"]

    response = client.get(
        f"{API}/registrations/{reg_id}", headers=auth_headers(user)
    )

    assert response.status_code == 200
    body = response.json()
    assert body["registration_status"] == "pending"
    assert body["attendance_status"] == "absent"
    assert body["student"]["student_id"] == "CS0012"
    assert body["student"]["department"] == "computer_science"
    assert body["event"]["name"] == event.name
    assert body["event"]["category"] == "workshop"
    assert body["event"]["max_participants"] == 30


def test_get_other_students_registration_forbidden(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session)
    owner = _create_student_user(db_session, email="reg13@example.com")
    other = _create_student_user(db_session, email="reg14@example.com")
    other_event = _create_event_in_db(db_session, name="Other Event")
    client.post(
        f"{API}/registrations",
        json=_registration_payload(
            str(other_event.id), "CS0014", email="other2@example.com"
        ),
        headers=auth_headers(other),
    )
    created = client.post(
        f"{API}/registrations",
        json=_registration_payload(str(event.id), "CS0013"),
        headers=auth_headers(owner),
    )
    reg_id = created.json()["id"]

    response = client.get(
        f"{API}/registrations/{reg_id}", headers=auth_headers(other)
    )

    assert response.status_code == 403


def test_get_registration_not_found(
    client: TestClient, db_session: Session
) -> None:
    user = _create_student_user(db_session, email="reg15@example.com")

    response = client.get(
        f"{API}/registrations/00000000-0000-0000-0000-000000000000",
        headers=auth_headers(user),
    )

    assert response.status_code == 404


# ---------------------------------------------------------- PUT /events/winners
def _winner_payload(
    event: Event,
    registrations: list[EventRegistration],
    *,
    names: tuple[str, str, str] = ("Alpha", "Beta", "Gamma"),
) -> list[dict]:
    """A payload for the three winner positions."""
    return [
        {
            "event_id": str(event.id),
            "registration_id": str(registrations[i].id),
            "position": position,
            "project_name": name,
            "project_url": f"http://example.com/{position}",
        }
        for i, (position, name) in enumerate(
            zip(("first", "second", "third"), names)
        )
    ]


def test_upsert_winners_creates_all_positions(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session, name="Winner Event")
    regs = [
        _create_registration_in_db(
            db_session, event=event, email=f"w1{i}@example.com", college_id=f"WC0{i}"
        )
        for i in range(3)
    ]
    admin = _create_admin(db_session, email="wadmin1@example.com")

    response = client.put(
        f"{API}/winners",
        json=_winner_payload(event, regs),
        headers=auth_headers(admin),
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 3
    positions = {winner["position"] for winner in body}
    assert positions == {"first", "second", "third"}
    assert next(
        winner["project_name"] for winner in body if winner["position"] == "first"
    ) == "Alpha"


def test_upsert_winners_updates_only_supplied_positions(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session, name="Winner Event")
    regs = [
        _create_registration_in_db(
            db_session, event=event, email=f"w2{i}@example.com", college_id=f"W1{i}"
        )
        for i in range(3)
    ]
    admin = _create_admin(db_session, email="wadmin2@example.com")

    full = client.put(
        f"{API}/winners",
        json=_winner_payload(event, regs),
        headers=auth_headers(admin),
    )
    assert full.status_code == 200

    partial = client.put(
        f"{API}/winners",
        json=[
            {
                "event_id": str(event.id),
                "registration_id": str(regs[0].id),
                "position": "first",
                "project_name": "Alpha-Updated",
            }
        ],
        headers=auth_headers(admin),
    )

    assert partial.status_code == 200
    body = partial.json()
    assert len(body) == 1
    assert body[0]["position"] == "first"
    assert body[0]["project_name"] == "Alpha-Updated"

    winners = db_session.scalars(select(EventWinner))
    by_position = {winner.position: winner.project_name for winner in winners}
    assert by_position[WinnerPosition.FIRST] == "Alpha-Updated"
    assert by_position[WinnerPosition.SECOND] == "Beta"
    assert by_position[WinnerPosition.THIRD] == "Gamma"


def test_upsert_winners_reassigns_position_registration(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session, name="Winner Event")
    regs = [
        _create_registration_in_db(
            db_session, event=event, email=f"w3a{i}@example.com", college_id=f"W30{i}"
        )
        for i in range(4)
    ]
    admin = _create_admin(db_session, email="wadmin3a@example.com")

    first = client.put(
        f"{API}/winners",
        json=_winner_payload(event, regs),
        headers=auth_headers(admin),
    )
    assert first.status_code == 200

    reassign = client.put(
        f"{API}/winners",
        json=[
            {
                "event_id": str(event.id),
                "registration_id": str(regs[3].id),
                "position": "first",
                "project_name": "Alpha-Reassigned",
            }
        ],
        headers=auth_headers(admin),
    )

    assert reassign.status_code == 200
    body = reassign.json()
    assert len(body) == 1
    assert body[0]["position"] == "first"
    assert body[0]["registration_id"] == str(regs[3].id)
    assert body[0]["project_name"] == "Alpha-Reassigned"

    winners = list(db_session.scalars(select(EventWinner)))
    by_position = {winner.position: winner for winner in winners}
    assert len(winners) == 3
    assert by_position[WinnerPosition.FIRST].registration_id == regs[3].id
    assert by_position[WinnerPosition.SECOND].registration_id == regs[1].id
    assert by_position[WinnerPosition.THIRD].registration_id == regs[2].id


def test_upsert_winners_event_not_found(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session, name="Winner Event")
    reg = _create_registration_in_db(
        db_session, event=event, email="w3@example.com", college_id="W20"
    )
    admin = _create_admin(db_session, email="wadmin3@example.com")

    response = client.put(
        f"{API}/winners",
        json=[
            {
                "event_id": "00000000-0000-0000-0000-000000000000",
                "registration_id": str(reg.id),
                "position": "first",
                "project_name": "X",
            }
        ],
        headers=auth_headers(admin),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_upsert_winners_registration_not_in_event(
    client: TestClient, db_session: Session
) -> None:
    event_a = _create_event_in_db(db_session, name="Event A")
    event_b = _create_event_in_db(db_session, name="Event B")
    reg = _create_registration_in_db(
        db_session, event=event_a, email="w4@example.com", college_id="W21"
    )
    admin = _create_admin(db_session, email="wadmin4@example.com")

    response = client.put(
        f"{API}/winners",
        json=[
            {
                "event_id": str(event_b.id),
                "registration_id": str(reg.id),
                "position": "first",
                "project_name": "X",
            }
        ],
        headers=auth_headers(admin),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Registration not found for this event"


def test_upsert_winners_student_forbidden(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session, name="Winner Event")
    reg = _create_registration_in_db(
        db_session, event=event, email="w5@example.com", college_id="W22"
    )
    student = _create_student_user(db_session, email="w5b@example.com")

    response = client.put(
        f"{API}/winners",
        json=_winner_payload(event, [reg, reg, reg]),
        headers=auth_headers(student),
    )

    assert response.status_code == 403


def test_upsert_winners_unauthenticated(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session, name="Winner Event")
    reg = _create_registration_in_db(
        db_session, event=event, email="w6@example.com", college_id="W23"
    )

    response = client.put(
        f"{API}/winners", json=_winner_payload(event, [reg, reg, reg])
    )

    assert response.status_code == 401


# ------------------------------------------ POST /events/winners
def test_declare_winner_for_registration_of_event(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session, name="Winner Event")
    reg = _create_registration_in_db(
        db_session, event=event, email="w66@example.com", college_id="W66"
    )
    admin = _create_admin(db_session, email="wadmin66@example.com")

    response = client.post(
        f"{API}/winners",
        json={
            "event_id": str(event.id),
            "registration_id": str(reg.id),
            "position": "first",
            "project_name": "Alpha",
        },
        headers=auth_headers(admin),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["event_id"] == str(event.id)
    assert body["registration_id"] == str(reg.id)
    assert body["project_name"] == "Alpha"


# ------------------------------------------ GET /events/{event_id}/winners
def test_get_event_winners_returns_all_positions(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session, name="Winner Event")
    regs = [
        _create_registration_in_db(
            db_session, event=event, email=f"g{i}@example.com", college_id=f"G0{i}"
        )
        for i in range(3)
    ]
    admin = _create_admin(db_session, email="gadmin@example.com")
    db_result = client.put(
        f"{API}/winners",
        json=_winner_payload(event, regs),
        headers=auth_headers(admin),
    )
    assert db_result.status_code == 200

    response = client.get(f"{API}/{event.id}/winners")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 3
    assert {winner["position"] for winner in body} == {
        "first",
        "second",
        "third",
    }


def test_get_event_winners_empty_when_none(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session, name="Winner Event")

    response = client.get(f"{API}/{event.id}/winners")

    assert response.status_code == 200
    assert response.json() == []


def test_get_event_winners_event_not_found(
    client: TestClient, db_session: Session
) -> None:
    response = client.get(f"{API}/00000000-0000-0000-0000-000000000000/winners")

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


# ---------------------------------------------------------- Certificate
def _create_registration_with_student(
    db: Session, *, event: Event, email: str, college_id: str
) -> tuple[User, Student, EventRegistration]:
    """Insert a student user, its Student profile and an event registration."""
    user = _create_student_user(db, email=email)
    student = Student(
        user_id=user.id,
        student_id=college_id,
        department=Department.COMPUTER_SCIENCE,
    )
    db.add(student)
    db.flush()
    registration = EventRegistration(
        event_id=event.id, student_id=student.id, team_name="Team"
    )
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return user, student, registration


def test_generate_certificates_for_event(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session, name="Cert Event")
    _, _, regs = zip(
        *[
            _create_registration_with_student(
                db_session, event=event, email=f"cert1{i}@example.com", college_id=f"C1{i}"
            )
            for i in range(3)
        ]
    )
    db_session.add(
        EventWinner(
            event_id=event.id,
            registration_id=regs[1].id,
            position=WinnerPosition.SECOND,
            project_name="Runner up",
        )
    )
    db_session.commit()
    admin = _create_admin(db_session, email="certadmin1@example.com")

    response = client.post(
        f"{API}/{event.id}/certificates", headers=auth_headers(admin)
    )

    assert response.status_code == 201
    body = response.json()
    assert len(body) == 3
    assert all(cert["certificate_url"] is None for cert in body)
    assert all(cert["event_name"] == "Cert Event" for cert in body)
    by_registration = {cert["registration_id"]: cert["certificate_type"] for cert in body}
    assert by_registration[str(regs[0].id)] == "participation"
    assert by_registration[str(regs[1].id)] == "second"
    assert by_registration[str(regs[2].id)] == "participation"


def test_generate_certificates_skips_existing(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session, name="Cert Event")
    for i in range(2):
        _create_registration_with_student(
            db_session, event=event, email=f"cert2{i}@example.com", college_id=f"C20{i}"
        )
    admin = _create_admin(db_session, email="cert2admin@example.com")

    first = client.post(
        f"{API}/{event.id}/certificates", headers=auth_headers(admin)
    )
    second = client.post(
        f"{API}/{event.id}/certificates", headers=auth_headers(admin)
    )

    assert first.status_code == 201
    assert len(first.json()) == 2
    assert second.status_code == 201
    assert second.json() == []


def test_generate_certificates_event_not_found(
    client: TestClient, db_session: Session
) -> None:
    admin = _create_admin(db_session, email="cert3@example.com")

    response = client.post(
        f"{API}/00000000-0000-0000-0000-000000000000/certificates",
        headers=auth_headers(admin),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_generate_certificates_no_registrations(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session, name="Cert Event")
    admin = _create_admin(db_session, email="cert4@example.com")

    response = client.post(
        f"{API}/{event.id}/certificates", headers=auth_headers(admin)
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "No registrations found for this event"


def test_generate_certificates_as_student_forbidden(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session, name="Cert Event")
    user, _, _ = _create_registration_with_student(
        db_session, event=event, email="cert5@example.com", college_id="C21"
    )

    response = client.post(
        f"{API}/{event.id}/certificates", headers=auth_headers(user)
    )

    assert response.status_code == 403


def test_generate_certificates_unauthenticated(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session, name="Cert Event")
    _create_registration_with_student(
        db_session, event=event, email="cert6@example.com", college_id="C22"
    )

    response = client.post(f"{API}/{event.id}/certificates")

    assert response.status_code == 401


def test_get_student_certificates(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session, name="Cert Event")
    user, student, _ = _create_registration_with_student(
        db_session, event=event, email="cert7@example.com", college_id="C23"
    )
    admin = _create_admin(db_session, email="cert7admin@example.com")
    client.post(f"{API}/{event.id}/certificates", headers=auth_headers(admin))

    response = client.get(
        f"{API.replace('events', 'students')}/{student.id}/certificates",
        headers=auth_headers(user),
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["certificate_type"] == "participation"
    assert body[0]["student_id"] == str(student.id)
    assert body[0]["event_name"] == "Cert Event"
    assert body[0]["student_name"] == "Stu"


def test_get_student_certificates_empty(
    client: TestClient, db_session: Session
) -> None:
    user = _create_student_user(db_session, email="cert8@example.com")
    student = Student(
        user_id=user.id,
        student_id="C24",
        department=Department.COMPUTER_SCIENCE,
    )
    db_session.add(student)
    db_session.commit()

    response = client.get(
        f"{API.replace('events', 'students')}/{student.id}/certificates",
        headers=auth_headers(user),
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_student_certificates_student_not_found(
    client: TestClient, db_session: Session
) -> None:
    user = _create_student_user(db_session, email="cert9@example.com")

    response = client.get(
        f"{API.replace('events', 'students')}/00000000-0000-0000-0000-000000000000/certificates",
        headers=auth_headers(user),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"


def test_get_student_certificates_as_admin_forbidden(
    client: TestClient, db_session: Session
) -> None:
    event = _create_event_in_db(db_session, name="Cert Event")
    _, student, _ = _create_registration_with_student(
        db_session, event=event, email="cert10@example.com", college_id="C25"
    )
    admin = _create_admin(db_session, email="cert10admin@example.com")

    response = client.get(
        f"{API.replace('events', 'students')}/{student.id}/certificates",
        headers=auth_headers(admin),
    )

    assert response.status_code == 403