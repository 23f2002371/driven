"""Integration tests for the Campus Bounties endpoints.

Each test is self-contained and creates its own data via the API or the
``db_session`` fixture, never relying on test execution order. The ``actual``
text of every request/response pair is recorded so the API test matrix shows
the real output, even when a test fails.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.bounty import Application, Bounty
from app.models.domain import Domain, StudentDomain, StudentTechnology, Technology
from app.models.student import Student
from app.models.user import User
from app.utils.enums import (
    BountyStatus,
    Department,
    DomainEnum,
    TechnologyEnum,
    UserRole,
)
from tests.conftest import auth_headers, record_actual

API = "/api"


# ------------------------------------------------------------- Helpers
def _admin(db: Session, *, email: str) -> User:
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


def _user_with_profile(
    db: Session, *, email: str, college_id: str
) -> tuple[User, Student]:
    """Create a student user together with its Student profile."""
    user = User(
        full_name="Student",
        email=email,
        password_hash=get_password_hash("testpassword123"),
        role=UserRole.STUDENT,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    student = Student(
        user_id=user.id,
        student_id=college_id,
        department=Department.COMPUTER_SCIENCE,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return user, student


def _user_without_profile(db: Session, *, email: str) -> User:
    """Create a student user with no linked Student profile."""
    user = User(
        full_name="Profileless",
        email=email,
        password_hash=get_password_hash("testpassword123"),
        role=UserRole.STUDENT,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _create_domain(db: Session, name: DomainEnum) -> Domain:
    """Insert a skill domain."""
    domain = Domain(name=name)
    db.add(domain)
    db.commit()
    db.refresh(domain)
    return domain


def _create_technology(db: Session, domain: Domain, name: TechnologyEnum) -> Technology:
    """Insert a technology under a domain."""
    technology = Technology(domain_id=domain.id, name=name)
    db.add(technology)
    db.commit()
    db.refresh(technology)
    return technology


def _add_student_skills(
    db: Session,
    *,
    student: Student,
    domain: Domain,
    technologies: list[Technology],
) -> None:
    """Attach a domain and its technologies to a student."""
    student_domain = StudentDomain(student_id=student.id, domain_id=domain.id)
    db.add(student_domain)
    db.flush()
    for technology in technologies:
        db.add(
            StudentTechnology(
                student_domain_id=student_domain.id,
                technology_id=technology.id,
            )
        )
    db.commit()
    db.refresh(student_domain)


def _bounty_payload(domain_id: UUID, **overrides: object) -> dict:
    """A minimal valid payload for creating a bounty."""
    payload: dict = {
        "title": "Build Club Website",
        "domain_id": str(domain_id),
        "description": "Build the student club website",
        "reward": "5000.00",
        "application_deadline": "2026-12-01T12:00:00Z",
        "duration": "2 weeks",
        "student_seats": 5,
        "image_url": None,
        "technologies": [],
        "responsibilities": ["Build landing page"],
    }
    payload.update(overrides)
    return payload


def _application_payload(**overrides: object) -> dict:
    """A minimal valid payload for applying to a bounty."""
    payload: dict = {
        "availability": "5 hours/week",
        "resume": "uploads/resume.pdf",
    }
    payload.update(overrides)
    return payload


def _work_payload(**overrides: object) -> dict:
    """A minimal valid payload for assigning work."""
    payload: dict = {
        "title": "Build landing page",
        "task_description": "Design and build the landing page",
        "deadline": "2026-12-01T12:00:00Z",
        "event_id": None,
        "deliverables": [
            {"title": "HTML page"},
            {"title": "CSS styles"},
        ],
    }
    payload.update(overrides)
    return payload


def _create_bounty_in_db(
    db: Session,
    *,
    admin: User,
    domain: Domain,
    status: BountyStatus = BountyStatus.OPEN,
    seats: int = 5,
    title: str = "Direct Bounty",
) -> Bounty:
    """Insert a bounty row directly, bypassing the API."""
    bounty = Bounty(
        title=title,
        domain_id=domain.id,
        description="Pre-seeded bounty for read tests.",
        reward=__import__("decimal").Decimal("5000.00"),
        application_deadline=datetime(2026, 12, 1, tzinfo=UTC),
        duration="2 weeks",
        student_seats=seats,
        image_url=None,
        status=status,
        created_by=admin.id,
    )
    db.add(bounty)
    db.commit()
    db.refresh(bounty)
    return bounty


def _apply_from(client: TestClient, bounty: Bounty, user: User, **overrides: object):
    """Apply to a bounty on behalf of a user."""
    return client.post(
        f"{API}/bounties/{bounty.id}/applications",
        json=_application_payload(**overrides),
        headers=auth_headers(user),
    )


def _accept_application(
    client: TestClient, application_id: str, admin: User
):
    """Accept an application as the club admin."""
    return client.patch(
        f"{API}/applications/{application_id}",
        json={"status": "accepted"},
        headers=auth_headers(admin),
    )


def _assign_work(client: TestClient, application_id: str, admin: User):
    """Assign work to an application as the club admin."""
    return client.post(
        f"{API}/applications/{application_id}/work",
        json=_work_payload(),
        headers=auth_headers(admin),
    )


def _setup_accepted_application(
    client: TestClient, db: Session, *, admin: User, student: User, bounty: Bounty
) -> str:
    """Apply and accept, returning the application id."""
    created = _apply_from(client, bounty, student)
    assert created.status_code == 201, created.text
    application_id = created.json()["id"]
    accepted = _accept_application(client, application_id, admin)
    assert accepted.status_code == 200, accepted.text
    return application_id


def _status_line(resp) -> str:
    """A short human description of a response for actual-output recording."""
    try:
        body = resp.json()
    except ValueError:
        body = resp.text or None
    return f"Status: {resp.status_code}, body: {body}"


# ------------------------------------------------------- POST /bounties
def test_create_bounty_success(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="bnadmin1@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    tech = _create_technology(db_session, domain, TechnologyEnum.REACT)

    response = client.post(
        f"{API}/bounties",
        json=_bounty_payload(
            domain.id,
            technologies=[str(tech.id)],
            responsibilities=["Build landing page", "Integrate API"],
        ),
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Build Club Website"
    assert body["status"] == "open"
    assert body["created_by"] == str(admin.id)
    assert body["created_by_name"] == "Admin"
    assert body["domain"]["name"] == "WEB_DEVELOPMENT"
    assert [t["name"] for t in body["technologies"]] == ["REACT"]
    assert {r["title"] for r in body["responsibilities"]} == {
        "Build landing page",
        "Integrate API",
    }


def test_create_bounty_as_student_forbidden(client: TestClient, db_session: Session) -> None:
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    student, _ = _user_with_profile(db_session, email="bn2@example.com", college_id="B2")

    response = client.post(
        f"{API}/bounties",
        json=_bounty_payload(domain.id),
        headers=auth_headers(student),
    )
    record_actual(_status_line(response))

    assert response.status_code == 403


def test_create_bounty_unauthenticated(client: TestClient, db_session: Session) -> None:
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)

    response = client.post(f"{API}/bounties", json=_bounty_payload(domain.id))
    record_actual(_status_line(response))

    assert response.status_code == 401


def test_create_bounty_domain_not_found(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="bn4@example.com")

    response = client.post(
        f"{API}/bounties",
        json=_bounty_payload("00000000-0000-0000-0000-000000000000"),
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 404
    assert response.json()["detail"] == "Domain not found"


def test_create_bounty_technology_not_found(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="bn5@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)

    response = client.post(
        f"{API}/bounties",
        json=_bounty_payload(
            domain.id,
            technologies=["00000000-0000-0000-0000-000000000000"],
        ),
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 404
    assert response.json()["detail"] == "Technology not found"


def test_create_bounty_technology_wrong_domain(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="bn6@example.com")
    web = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    ml = _create_domain(db_session, DomainEnum.AI_ML)
    pytorch = _create_technology(db_session, ml, TechnologyEnum.PYTORCH)

    response = client.post(
        f"{API}/bounties",
        json=_bounty_payload(web.id, technologies=[str(pytorch.id)]),
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 400
    assert response.json()["detail"] == "Technology does not belong to the selected domain"


def test_create_bounty_status_field_rejected(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="bn7@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)

    response = client.post(
        f"{API}/bounties",
        json=_bounty_payload(domain.id, status="closed", created_by=str(admin.id)),
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 422


def test_create_bounty_missing_required_field(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="bn8@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    payload = _bounty_payload(domain.id)
    del payload["description"]

    response = client.post(
        f"{API}/bounties", json=payload, headers=auth_headers(admin)
    )
    record_actual(_status_line(response))

    assert response.status_code == 422


def test_create_bounty_negative_reward(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="bn9@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)

    response = client.post(
        f"{API}/bounties",
        json=_bounty_payload(domain.id, reward="-100"),
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 422


# ------------------------------------------------------- PATCH /bounties/{id}
def test_update_bounty_fields_success(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="bn10@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)

    response = client.patch(
        f"{API}/bounties/{bounty.id}",
        json={"title": "Updated Title", "student_seats": 8},
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Updated Title"
    assert body["student_seats"] == 8
    assert body["status"] == "open"


def test_update_bounty_as_student_forbidden(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="bn11@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(db_session, email="bn11s@example.com", college_id="B11S")

    response = client.patch(
        f"{API}/bounties/{bounty.id}",
        json={"title": "Hacked"},
        headers=auth_headers(student),
    )
    record_actual(_status_line(response))

    assert response.status_code == 403


def test_update_bounty_not_found(client: TestClient, db_session: Session) -> None:
    admin = _admin(db_session, email="bn12@example.com")

    response = client.patch(
        f"{API}/bounties/00000000-0000-0000-0000-000000000000",
        json={"title": "Nope"},
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 404
    assert response.json()["detail"] == "Bounty not found"


def test_update_bounty_status_field_rejected(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="bn13@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)

    response = client.patch(
        f"{API}/bounties/{bounty.id}",
        json={"status": "closed", "created_by": str(admin.id), "id": str(bounty.id)},
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 422


def test_update_bounty_replaces_technologies(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="bn14@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    react = _create_technology(db_session, domain, TechnologyEnum.REACT)
    typescript = _create_technology(db_session, domain, TechnologyEnum.TYPESCRIPT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    bounty.technologies = [__import__("app.models.bounty", fromlist=["BountyTechnology"]).BountyTechnology(technology_id=react.id)]
    db_session.commit()

    response = client.patch(
        f"{API}/bounties/{bounty.id}",
        json={"technologies": [str(typescript.id)]},
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 200
    body = response.json()
    assert [t["name"] for t in body["technologies"]] == ["TYPESCRIPT"]


def test_update_bounty_replaces_responsibilities(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="bn15@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)

    response = client.patch(
        f"{API}/bounties/{bounty.id}",
        json={"responsibilities": ["Design", "Develop", "Deploy"]},
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 200
    body = response.json()
    assert sorted(r["title"] for r in body["responsibilities"]) == [
        "Deploy",
        "Design",
        "Develop",
    ]


def test_update_bounty_technology_wrong_domain(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="bn16@example.com")
    web = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    ml = _create_domain(db_session, DomainEnum.AI_ML)
    pytorch = _create_technology(db_session, ml, TechnologyEnum.PYTORCH)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=web)

    response = client.patch(
        f"{API}/bounties/{bounty.id}",
        json={"technologies": [str(pytorch.id)]},
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 400


def test_update_bounty_domain_changed_success(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="bn17@example.com")
    web = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    ml = _create_domain(db_session, DomainEnum.AI_ML)
    next_js = _create_technology(db_session, ml, TechnologyEnum.NEXT_JS)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=web)

    response = client.patch(
        f"{API}/bounties/{bounty.id}",
        json={"domain_id": str(ml.id), "technologies": [str(next_js.id)]},
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 200
    body = response.json()
    assert body["domain"]["name"] == "AI_ML"
    assert [t["name"] for t in body["technologies"]] == ["NEXT_JS"]


def test_update_bounty_domain_changed_wrong_technology(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="bn18@example.com")
    web = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    ml = _create_domain(db_session, DomainEnum.AI_ML)
    react = _create_technology(db_session, web, TechnologyEnum.REACT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=web)
    bounty.technologies = [__import__("app.models.bounty", fromlist=["BountyTechnology"]).BountyTechnology(technology_id=react.id)]
    db_session.commit()

    response = client.patch(
        f"{API}/bounties/{bounty.id}",
        json={"domain_id": str(ml.id), "technologies": [str(react.id)]},
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 400


# ------------------------------------------------------- GET /bounties/{id}
def test_get_bounty_success(client: TestClient, db_session: Session) -> None:
    admin = _admin(db_session, email="bn19@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    tech = _create_technology(db_session, domain, TechnologyEnum.REACT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    bounty.technologies = [__import__("app.models.bounty", fromlist=["BountyTechnology"]).BountyTechnology(technology_id=tech.id)]
    db_session.add(__import__("app.models.bounty", fromlist=["Responsibility"]).Responsibility(bounty_id=bounty.id, title="Build"))
    db_session.commit()

    student, _ = _user_with_profile(db_session, email="bn19s@example.com", college_id="B19S")

    response = client.get(
        f"{API}/bounties/{bounty.id}", headers=auth_headers(student)
    )
    record_actual(_status_line(response))

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Direct Bounty"
    assert body["status"] == "open"
    assert body["domain"]["name"] == "WEB_DEVELOPMENT"
    assert [t["name"] for t in body["technologies"]] == ["REACT"]
    assert body["created_by_name"] == "Admin"


def test_get_bounty_as_admin_or_lab_admin(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="bn20@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    lab_admin = User(
        full_name="Lab",
        email="bn20lab@example.com",
        password_hash=get_password_hash("testpassword123"),
        role=UserRole.LAB_ADMIN,
    )
    db_session.add(lab_admin)
    db_session.commit()
    db_session.refresh(lab_admin)

    response = client.get(
        f"{API}/bounties/{bounty.id}", headers=auth_headers(lab_admin)
    )
    record_actual(_status_line(response))

    assert response.status_code == 200


def test_get_bounty_not_found(client: TestClient, db_session: Session) -> None:
    student, _ = _user_with_profile(db_session, email="bn21@example.com", college_id="B21")

    response = client.get(
        f"{API}/bounties/00000000-0000-0000-0000-000000000000",
        headers=auth_headers(student),
    )
    record_actual(_status_line(response))

    assert response.status_code == 404
    assert response.json()["detail"] == "Bounty not found"


def test_get_bounty_unauthenticated(client: TestClient, db_session: Session) -> None:
    admin = _admin(db_session, email="bn22@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)

    response = client.get(f"{API}/bounties/{bounty.id}")
    record_actual(_status_line(response))

    assert response.status_code == 401


# ------------------------------------------------------- DELETE /bounties/{id}
def test_delete_bounty_success(client: TestClient, db_session: Session) -> None:
    admin = _admin(db_session, email="bn23@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)

    response = client.delete(
        f"{API}/bounties/{bounty.id}", headers=auth_headers(admin)
    )
    record_actual(_status_line(response))

    assert response.status_code == 204
    deleted = db_session.scalar(
        select(Bounty.id).where(Bounty.id == bounty.id)
    )
    assert deleted is None


def test_delete_bounty_as_student_forbidden(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="bn24@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(db_session, email="bn24s@example.com", college_id="B24S")

    response = client.delete(
        f"{API}/bounties/{bounty.id}", headers=auth_headers(student)
    )
    record_actual(_status_line(response))

    assert response.status_code == 403


def test_delete_bounty_not_found(client: TestClient, db_session: Session) -> None:
    admin = _admin(db_session, email="bn25@example.com")

    response = client.delete(
        f"{API}/bounties/00000000-0000-0000-0000-000000000000",
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 404
    assert response.json()["detail"] == "Bounty not found"


# ----------------------------------- POST /bounties/{bounty_id}/applications
def test_create_application_success(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="app1@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, student_row = _user_with_profile(
        db_session, email="app1s@example.com", college_id="A1S"
    )

    response = _apply_from(client, bounty, student)
    record_actual(_status_line(response))

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["student_id"] == str(student_row.id)
    assert body["availability"] == "5 hours/week"
    assert body["resume"] == "uploads/resume.pdf"
    assert body["bounty"]["title"] == "Direct Bounty"
    assert body["student"]["student_id"] == "A1S"


def test_create_application_status_field_rejected(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="app2@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(db_session, email="app2s@example.com", college_id="A2S")

    response = _apply_from(
        client, bounty, student, status="accepted", student_id="00000000-0000-0000-0000-000000000000"
    )
    record_actual(_status_line(response))

    assert response.status_code == 422


def test_create_application_as_admin_forbidden(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="app3@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)

    response = _apply_from(client, bounty, admin)
    record_actual(_status_line(response))

    assert response.status_code == 403


def test_create_application_unauthenticated(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="app4@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)

    response = client.post(
        f"{API}/bounties/{bounty.id}/applications", json=_application_payload()
    )
    record_actual(_status_line(response))

    assert response.status_code == 401


def test_create_application_bounty_not_found(
    client: TestClient, db_session: Session
) -> None:
    student, _ = _user_with_profile(db_session, email="app5@example.com", college_id="A5")

    response = client.post(
        f"{API}/bounties/00000000-0000-0000-0000-000000000000/applications",
        json=_application_payload(),
        headers=auth_headers(student),
    )
    record_actual(_status_line(response))

    assert response.status_code == 404
    assert response.json()["detail"] == "Bounty not found"


def test_create_application_closed_bounty(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="app6@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(
        db_session, admin=admin, domain=domain, status=BountyStatus.CLOSED
    )
    student, _ = _user_with_profile(db_session, email="app6s@example.com", college_id="A6S")

    response = _apply_from(client, bounty, student)
    record_actual(_status_line(response))

    assert response.status_code == 409
    assert response.json()["detail"] == "Bounty is not accepting applications"


def test_create_application_duplicate(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="app7@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(db_session, email="app7s@example.com", college_id="A7S")

    first = _apply_from(client, bounty, student)
    second = _apply_from(client, bounty, student)
    record_actual("first: " + _status_line(first) + " | second: " + _status_line(second))

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["detail"] == "You have already applied to this bounty"


def test_create_application_no_student_profile(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="app8@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student = _user_without_profile(db_session, email="app8s@example.com")

    response = _apply_from(client, bounty, student)
    record_actual(_status_line(response))

    assert response.status_code == 404
    assert response.json()["detail"] == "Student profile not found"


def test_create_application_missing_availability(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="app9@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(db_session, email="app9s@example.com", college_id="A9S")

    response = client.post(
        f"{API}/bounties/{bounty.id}/applications",
        json={"resume": "uploads/resume.pdf"},
        headers=auth_headers(student),
    )
    record_actual(_status_line(response))

    assert response.status_code == 422


# ----------------------------------------------- GET /applications/{id}
def test_get_application_as_owner(client: TestClient, db_session: Session) -> None:
    admin = _admin(db_session, email="app10@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(
        db_session, email="app10s@example.com", college_id="A10S"
    )
    application_id = _setup_accepted_application(
        client, db_session, admin=admin, student=student, bounty=bounty
    )

    response = client.get(
        f"{API}/applications/{application_id}", headers=auth_headers(student)
    )
    record_actual(_status_line(response))

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "accepted"
    assert body["bounty"]["title"] == "Direct Bounty"
    assert body["student"]["name"] == "Student"


def test_get_application_as_admin(client: TestClient, db_session: Session) -> None:
    admin = _admin(db_session, email="app11@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(
        db_session, email="app11s@example.com", college_id="A11S"
    )
    application_id = _setup_accepted_application(
        client, db_session, admin=admin, student=student, bounty=bounty
    )

    response = client.get(
        f"{API}/applications/{application_id}", headers=auth_headers(admin)
    )
    record_actual(_status_line(response))

    assert response.status_code == 200


def test_get_application_as_other_student(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="app12@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    owner, _ = _user_with_profile(
        db_session, email="app12o@example.com", college_id="A12O"
    )
    other, _ = _user_with_profile(
        db_session, email="app12s@example.com", college_id="A12S"
    )
    application_id = _setup_accepted_application(
        client, db_session, admin=admin, student=owner, bounty=bounty
    )

    response = client.get(
        f"{API}/applications/{application_id}", headers=auth_headers(other)
    )
    record_actual(_status_line(response))

    assert response.status_code == 403


def test_get_application_not_found(client: TestClient, db_session: Session) -> None:
    admin = _admin(db_session, email="app13@example.com")

    response = client.get(
        f"{API}/applications/00000000-0000-0000-0000-000000000000",
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"


def test_get_application_unauthenticated(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="app14@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(
        db_session, email="app14s@example.com", college_id="A14S"
    )
    application_id = _setup_accepted_application(
        client, db_session, admin=admin, student=student, bounty=bounty
    )

    response = client.get(f"{API}/applications/{application_id}")
    record_actual(_status_line(response))

    assert response.status_code == 401


# ------------------------------------------------ PATCH /applications/{id}
def test_update_application_status_accepted(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="app15@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain, seats=2)
    student, _ = _user_with_profile(
        db_session, email="app15s@example.com", college_id="A15S"
    )
    created = _apply_from(client, bounty, student)
    application_id = created.json()["id"]

    response = client.patch(
        f"{API}/applications/{application_id}",
        json={"status": "accepted"},
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


def test_update_application_status_rejected(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="app16@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(
        db_session, email="app16s@example.com", college_id="A16S"
    )
    created = _apply_from(client, bounty, student)
    application_id = created.json()["id"]

    response = client.patch(
        f"{API}/applications/{application_id}",
        json={"status": "rejected"},
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"


def test_update_application_as_student_forbidden(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="app17@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(
        db_session, email="app17s@example.com", college_id="A17S"
    )
    application_id = _setup_accepted_application(
        client, db_session, admin=admin, student=student, bounty=bounty
    )

    response = client.patch(
        f"{API}/applications/{application_id}",
        json={"status": "rejected"},
        headers=auth_headers(student),
    )
    record_actual(_status_line(response))

    assert response.status_code == 403


def test_update_application_not_found(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="app18@example.com")

    response = client.patch(
        f"{API}/applications/00000000-0000-0000-0000-000000000000",
        json={"status": "accepted"},
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"


def test_update_application_extra_field_rejected(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="app19@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(
        db_session, email="app19s@example.com", college_id="A19S"
    )
    created = _apply_from(client, bounty, student)
    application_id = created.json()["id"]

    response = client.patch(
        f"{API}/applications/{application_id}",
        json={"status": "accepted", "availability": "10 hours/week"},
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 422


def test_update_application_seat_limit_conflict(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="app20@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain, seats=1)
    first, _ = _user_with_profile(
        db_session, email="app20a@example.com", college_id="A20A"
    )
    second, _ = _user_with_profile(
        db_session, email="app20b@example.com", college_id="A20B"
    )
    first_app = _apply_from(client, bounty, first).json()["id"]
    second_app = _apply_from(client, bounty, second).json()["id"]

    accept_first = _accept_application(client, first_app, admin)
    accept_second = _accept_application(client, second_app, admin)
    record_actual(
        "first: " + _status_line(accept_first) + " | second: " + _status_line(accept_second)
    )

    assert accept_first.status_code == 200
    assert accept_second.status_code == 409
    assert accept_second.json()["detail"] == "All seats for this bounty are filled"


def test_reaccepting_application_does_not_consume_another_seat(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="app21@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain, seats=1)
    student, _ = _user_with_profile(
        db_session, email="app21s@example.com", college_id="A21S"
    )
    application_id = _setup_accepted_application(
        client, db_session, admin=admin, student=student, bounty=bounty
    )

    response = client.patch(
        f"{API}/applications/{application_id}",
        json={"status": "accepted"},
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 200

# ------------------------------------------------ DELETE /applications/{id}
def test_delete_rejected_application_success(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="app22@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(
        db_session, email="app22s@example.com", college_id="A22S"
    )
    created = _apply_from(client, bounty, student)
    application_id = created.json()["id"]
    client.patch(
        f"{API}/applications/{application_id}",
        json={"status": "rejected"},
        headers=auth_headers(admin),
    )

    response = client.delete(
        f"{API}/applications/{application_id}", headers=auth_headers(student)
    )
    record_actual(_status_line(response))

    assert response.status_code == 204
    assert db_session.get(Application, UUID(application_id)) is None


def test_delete_pending_application_conflict(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="app23@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(
        db_session, email="app23s@example.com", college_id="A23S"
    )
    created = _apply_from(client, bounty, student)
    application_id = created.json()["id"]

    response = client.delete(
        f"{API}/applications/{application_id}", headers=auth_headers(student)
    )
    record_actual(_status_line(response))

    assert response.status_code == 409
    assert response.json()["detail"] == "Only a rejected application can be deleted"


def test_delete_other_students_application_forbidden(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="app24@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    owner, _ = _user_with_profile(
        db_session, email="app24o@example.com", college_id="A24O"
    )
    other, _ = _user_with_profile(
        db_session, email="app24s@example.com", college_id="A24S"
    )
    created = _apply_from(client, bounty, owner)
    application_id = created.json()["id"]
    client.patch(
        f"{API}/applications/{application_id}",
        json={"status": "rejected"},
        headers=auth_headers(admin),
    )

    response = client.delete(
        f"{API}/applications/{application_id}", headers=auth_headers(other)
    )
    record_actual(_status_line(response))

    assert response.status_code == 403


def test_delete_application_as_admin_forbidden(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="app25@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(
        db_session, email="app25s@example.com", college_id="A25S"
    )
    created = _apply_from(client, bounty, student)
    application_id = created.json()["id"]
    client.patch(
        f"{API}/applications/{application_id}",
        json={"status": "rejected"},
        headers=auth_headers(admin),
    )

    response = client.delete(
        f"{API}/applications/{application_id}", headers=auth_headers(admin)
    )
    record_actual(_status_line(response))

    assert response.status_code == 403


def test_delete_application_not_found(
    client: TestClient, db_session: Session
) -> None:
    student, _ = _user_with_profile(db_session, email="app26@example.com", college_id="A26")

    response = client.delete(
        f"{API}/applications/00000000-0000-0000-0000-000000000000",
        headers=auth_headers(student),
    )
    record_actual(_status_line(response))

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"


# ----------------------------------- POST /applications/{id}/work
def test_assign_work_success(client: TestClient, db_session: Session) -> None:
    admin = _admin(db_session, email="wrk1@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(db_session, email="wrk1s@example.com", college_id="W1S")
    application_id = _setup_accepted_application(
        client, db_session, admin=admin, student=student, bounty=bounty
    )

    response = _assign_work(client, application_id, admin)
    record_actual(_status_line(response))

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "assigned"
    assert body["title"] == "Build landing page"
    assert body["application"]["status"] == "accepted"
    assert body["application"]["student_name"] == "Student"
    assert {d["status"] for d in body["deliverables"]} == {"pending"}


def test_assign_work_to_pending_application(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="wrk2@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(db_session, email="wrk2s@example.com", college_id="W2S")
    created = _apply_from(client, bounty, student)
    application_id = created.json()["id"]

    response = _assign_work(client, application_id, admin)
    record_actual(_status_line(response))

    assert response.status_code == 409
    assert response.json()["detail"] == "Only an accepted application can receive work"


def test_assign_work_to_rejected_application(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="wrk3@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(db_session, email="wrk3s@example.com", college_id="W3S")
    created = _apply_from(client, bounty, student)
    application_id = created.json()["id"]
    client.patch(
        f"{API}/applications/{application_id}",
        json={"status": "rejected"},
        headers=auth_headers(admin),
    )

    response = _assign_work(client, application_id, admin)
    record_actual(_status_line(response))

    assert response.status_code == 409


def test_assign_work_already_assigned(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="wrk4@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(db_session, email="wrk4s@example.com", college_id="W4S")
    application_id = _setup_accepted_application(
        client, db_session, admin=admin, student=student, bounty=bounty
    )
    first = _assign_work(client, application_id, admin)
    second = _assign_work(client, application_id, admin)
    record_actual(
        "first: " + _status_line(first) + " | second: " + _status_line(second)
    )

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["detail"] == "Work is already assigned to this application"


def test_assign_work_as_student_forbidden(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="wrk5@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(db_session, email="wrk5s@example.com", college_id="W5S")
    application_id = _setup_accepted_application(
        client, db_session, admin=admin, student=student, bounty=bounty
    )

    response = _assign_work(client, application_id, student)
    record_actual(_status_line(response))

    assert response.status_code == 403


def test_assign_work_application_not_found(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="wrk6@example.com")

    response = client.post(
        f"{API}/applications/00000000-0000-0000-0000-000000000000/work",
        json=_work_payload(),
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"


def test_assign_work_event_not_found(client: TestClient, db_session: Session) -> None:
    admin = _admin(db_session, email="wrk7@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(db_session, email="wrk7s@example.com", college_id="W7S")
    application_id = _setup_accepted_application(
        client, db_session, admin=admin, student=student, bounty=bounty
    )

    response = client.post(
        f"{API}/applications/{application_id}/work",
        json=_work_payload(event_id="00000000-0000-0000-0000-000000000000"),
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


# ----------------------------------- GET /applications/{id}/work
def test_get_assigned_work_as_owner(client: TestClient, db_session: Session) -> None:
    admin = _admin(db_session, email="wrk8@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(db_session, email="wrk8s@example.com", college_id="W8S")
    application_id = _setup_accepted_application(
        client, db_session, admin=admin, student=student, bounty=bounty
    )
    _assign_work(client, application_id, admin)

    response = client.get(
        f"{API}/applications/{application_id}/work", headers=auth_headers(student)
    )
    record_actual(_status_line(response))

    assert response.status_code == 200
    body = response.json()
    assert body["application_id"] == application_id
    assert body["application"]["student_name"] == "Student"
    assert len(body["deliverables"]) == 2


def test_get_assigned_work_as_admin(client: TestClient, db_session: Session) -> None:
    admin = _admin(db_session, email="wrk9@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(db_session, email="wrk9s@example.com", college_id="W9S")
    application_id = _setup_accepted_application(
        client, db_session, admin=admin, student=student, bounty=bounty
    )
    _assign_work(client, application_id, admin)

    response = client.get(
        f"{API}/applications/{application_id}/work", headers=auth_headers(admin)
    )
    record_actual(_status_line(response))

    assert response.status_code == 200


def test_get_assigned_work_as_other_student(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="wrk10@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    owner, _ = _user_with_profile(db_session, email="wrk10o@example.com", college_id="W10O")
    other, _ = _user_with_profile(db_session, email="wrk10s@example.com", college_id="W10S")
    application_id = _setup_accepted_application(
        client, db_session, admin=admin, student=owner, bounty=bounty
    )
    _assign_work(client, application_id, admin)

    response = client.get(
        f"{API}/applications/{application_id}/work", headers=auth_headers(other)
    )
    record_actual(_status_line(response))

    assert response.status_code == 403


def test_get_assigned_work_not_assigned(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="wrk11@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(db_session, email="wrk11s@example.com", college_id="W11S")
    application_id = _setup_accepted_application(
        client, db_session, admin=admin, student=student, bounty=bounty
    )

    response = client.get(
        f"{API}/applications/{application_id}/work", headers=auth_headers(admin)
    )
    record_actual(_status_line(response))

    assert response.status_code == 404
    assert response.json()["detail"] == "Work not found for this application"


def test_get_assigned_work_application_not_found(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="wrk12@example.com")

    response = client.get(
        f"{API}/applications/00000000-0000-0000-0000-000000000000/work",
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"


# ----------------------------------- PATCH /applications/{id}/work
def _setup_work(client: TestClient, db_session: Session, *, admin: User, student: User, bounty: Bounty) -> tuple[str, dict]:
    """Apply, accept, assign work; return the work body (with deliverable ids)."""
    application_id = _setup_accepted_application(
        client, db_session, admin=admin, student=student, bounty=bounty
    )
    work = _assign_work(client, application_id, admin)
    assert work.status_code == 201, work.text
    return application_id, work.json()


def test_student_updates_work_status(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="wrk13@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(db_session, email="wrk13s@example.com", college_id="W13S")
    application_id, _ = _setup_work(client, db_session, admin=admin, student=student, bounty=bounty)

    response = client.patch(
        f"{API}/applications/{application_id}/work",
        json={"status": "in_progress"},
        headers=auth_headers(student),
    )
    record_actual(_status_line(response))

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_student_updates_deliverable_status(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="wrk14@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(db_session, email="wrk14s@example.com", college_id="W14S")
    application_id, work = _setup_work(
        client, db_session, admin=admin, student=student, bounty=bounty
    )
    deliverable_id = work["deliverables"][0]["id"]

    response = client.patch(
        f"{API}/applications/{application_id}/work",
        json={"deliverables": [{"id": deliverable_id, "status": "completed"}]},
        headers=auth_headers(student),
    )
    record_actual(_status_line(response))

    assert response.status_code == 200
    by_id = {d["id"]: d["status"] for d in response.json()["deliverables"]}
    assert by_id[deliverable_id] == "completed"


def test_student_cannot_update_title(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="wrk15@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(db_session, email="wrk15s@example.com", college_id="W15S")
    application_id, _ = _setup_work(
        client, db_session, admin=admin, student=student, bounty=bounty
    )

    response = client.patch(
        f"{API}/applications/{application_id}/work",
        json={"title": "Hacked"},
        headers=auth_headers(student),
    )
    record_actual(_status_line(response))

    assert response.status_code == 422


def test_admin_updates_work_details(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="wrk16@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(db_session, email="wrk16s@example.com", college_id="W16S")
    application_id, _ = _setup_work(
        client, db_session, admin=admin, student=student, bounty=bounty
    )

    response = client.patch(
        f"{API}/applications/{application_id}/work",
        json={
            "title": "Redesign",
            "task_description": "Redo the design",
            "deadline": "2026-12-15T12:00:00Z",
            "status": "in_progress",
        },
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Redesign"
    assert body["task_description"] == "Redo the design"
    assert body["status"] == "in_progress"


def test_admin_updates_deliverable_status(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="wrk17@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(db_session, email="wrk17s@example.com", college_id="W17S")
    application_id, work = _setup_work(
        client, db_session, admin=admin, student=student, bounty=bounty
    )
    deliverable_id = work["deliverables"][0]["id"]

    response = client.patch(
        f"{API}/applications/{application_id}/work",
        json={"deliverables": [{"id": deliverable_id, "status": "in_progress"}]},
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 200
    by_id = {d["id"]: d["status"] for d in response.json()["deliverables"]}
    assert by_id[deliverable_id] == "in_progress"


def test_admin_cannot_change_application_id(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="wrk18@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(db_session, email="wrk18s@example.com", college_id="W18S")
    application_id, _ = _setup_work(
        client, db_session, admin=admin, student=student, bounty=bounty
    )

    response = client.patch(
        f"{API}/applications/{application_id}/work",
        json={"application_id": "00000000-0000-0000-0000-000000000000"},
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 422


def test_admin_updates_event_id(client: TestClient, db_session: Session) -> None:
    from app.models.event import Event

    admin = _admin(db_session, email="wrk19@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(db_session, email="wrk19s@example.com", college_id="W19S")
    application_id, _ = _setup_work(
        client, db_session, admin=admin, student=student, bounty=bounty
    )
    event = Event(
        name="Hackathon",
        short_description="24h hackathon",
        category="hackathon",
        event_date=datetime(2026, 12, 5, tzinfo=UTC).date(),
        registration_deadline=datetime(2026, 11, 20, tzinfo=UTC),
        venue="auditorium",
        max_participants=50,
        description="Build in 24h",
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    response = client.patch(
        f"{API}/applications/{application_id}/work",
        json={"event_id": str(event.id)},
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 200
    assert response.json()["event"] == {
        "id": str(event.id),
        "name": "Hackathon",
    }


def test_admin_invalid_event_not_found(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="wrk20@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(db_session, email="wrk20s@example.com", college_id="W20S")
    application_id, _ = _setup_work(
        client, db_session, admin=admin, student=student, bounty=bounty
    )

    response = client.patch(
        f"{API}/applications/{application_id}/work",
        json={"event_id": "00000000-0000-0000-0000-000000000000"},
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_other_student_update_forbidden(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="wrk21@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    owner, _ = _user_with_profile(db_session, email="wrk21o@example.com", college_id="W21O")
    other, _ = _user_with_profile(db_session, email="wrk21s@example.com", college_id="W21S")
    application_id, _ = _setup_work(
        client, db_session, admin=admin, student=owner, bounty=bounty
    )

    response = client.patch(
        f"{API}/applications/{application_id}/work",
        json={"status": "completed"},
        headers=auth_headers(other),
    )
    record_actual(_status_line(response))

    assert response.status_code == 403


def test_update_work_unknown_deliverable(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="wrk22@example.com")
    domain = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    bounty = _create_bounty_in_db(db_session, admin=admin, domain=domain)
    student, _ = _user_with_profile(db_session, email="wrk22s@example.com", college_id="W22S")
    application_id, _ = _setup_work(
        client, db_session, admin=admin, student=student, bounty=bounty
    )

    response = client.patch(
        f"{API}/applications/{application_id}/work",
        json={"deliverables": [{"id": "00000000-0000-0000-0000-000000000000", "status": "completed"}]},
        headers=auth_headers(student),
    )
    record_actual(_status_line(response))

    assert response.status_code == 404
    assert response.json()["detail"] == "Deliverable not found"


# ------------------------------------------------ GET /students/me/skills
def test_get_my_skills_success(client: TestClient, db_session: Session) -> None:
    student, student_row = _user_with_profile(
        db_session, email="sky1@example.com", college_id="S1"
    )
    web = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    react = _create_technology(db_session, web, TechnologyEnum.REACT)
    node = _create_technology(db_session, web, TechnologyEnum.NODE_JS)
    _add_student_skills(
        db_session, student=student_row, domain=web, technologies=[react, node]
    )

    response = client.get(
        f"{API}/students/me/skills", headers=auth_headers(student)
    )
    record_actual(_status_line(response))

    assert response.status_code == 200
    body = response.json()
    assert body == [
        {
            "domain": "WEB_DEVELOPMENT",
            "technologies": [{"technology": "REACT"}, {"technology": "NODE_JS"}],
        }
    ]


def test_get_my_skills_success_with_multiple_domains(
    client: TestClient, db_session: Session
) -> None:
    student, student_row = _user_with_profile(
        db_session, email="sky2@example.com", college_id="S2"
    )
    web = _create_domain(db_session, DomainEnum.WEB_DEVELOPMENT)
    ml = _create_domain(db_session, DomainEnum.AI_ML)
    react = _create_technology(db_session, web, TechnologyEnum.REACT)
    pytorch = _create_technology(db_session, ml, TechnologyEnum.PYTORCH)
    _add_student_skills(db_session, student=student_row, domain=web, technologies=[react])
    _add_student_skills(db_session, student=student_row, domain=ml, technologies=[pytorch])

    response = client.get(
        f"{API}/students/me/skills", headers=auth_headers(student)
    )
    record_actual(_status_line(response))

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    by_domain = {item["domain"]: item["technologies"] for item in body}
    assert by_domain["WEB_DEVELOPMENT"] == [{"technology": "REACT"}]
    assert by_domain["AI_ML"] == [{"technology": "PYTORCH"}]


def test_get_my_skills_empty(client: TestClient, db_session: Session) -> None:
    student, _ = _user_with_profile(db_session, email="sky3@example.com", college_id="S3")

    response = client.get(
        f"{API}/students/me/skills", headers=auth_headers(student)
    )
    record_actual(_status_line(response))

    assert response.status_code == 200
    assert response.json() == []


def test_get_my_skills_no_profile(client: TestClient, db_session: Session) -> None:
    student = _user_without_profile(db_session, email="sky4@example.com")

    response = client.get(
        f"{API}/students/me/skills", headers=auth_headers(student)
    )
    record_actual(_status_line(response))

    assert response.status_code == 404
    assert response.json()["detail"] == "Student profile not found"


def test_get_my_skills_as_admin_forbidden(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="sky5@example.com")

    response = client.get(f"{API}/students/me/skills", headers=auth_headers(admin))
    record_actual(_status_line(response))

    assert response.status_code == 403