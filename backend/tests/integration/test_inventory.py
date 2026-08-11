"""Integration tests for the inventory endpoints.

Each test is self-contained and creates its own data via the API or the
``db_session`` fixture, never relying on test execution order. The ``actual``
text of every request/response pair is recorded so the API test matrix shows
the real output, even when a test fails.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.inventory import BorrowDetail, Equipment
from app.models.student import Student
from app.models.user import User
from app.utils.enums import Department, UserRole
from tests.conftest import auth_headers, record_actual

API = "/api/equipment"


def _valid_equipment_payload(**overrides: object) -> dict:
    """A minimal valid payload for creating equipment."""
    payload: dict = {
        "name": "Oscilloscope",
        "category": "electronics",
        "description": "100 MHz digital oscilloscope",
        "total_quantity": 10,
        "available_quantity": 10,
        "storage_location": "Lab A",
        "equipment_image_url": None,
    }
    payload.update(overrides)
    return payload


def _create_equipment_in_db(db: Session, name: str = "Oscilloscope") -> Equipment:
    """Insert an equipment row directly, bypassing the API."""
    equipment = Equipment(
        name=name,
        category="electronics",
        description="Pre-seeded equipment for tests.",
        total_quantity=10,
        available_quantity=10,
        storage_location="Lab A",
    )
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    return equipment


def _borrow_payload(equipment_id: str, **overrides: object) -> dict:
    """A minimal valid borrow payload."""
    payload: dict = {
        "equipment_id": equipment_id,
        "borrowed_quantity": 2,
        "return_date": "2026-12-01T12:00:00Z",
    }
    payload.update(overrides)
    return payload


def _user_with_profile(db: Session, *, email: str) -> User:
    """Create a student user together with its Student profile.

    The returned user exposes ``.student`` once the relationship is loaded.
    """
    user = User(
        full_name="Borrower",
        email=email,
        password_hash=get_password_hash("testpassword123"),
        role=UserRole.STUDENT,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    student = Student(
        user_id=user.id,
        student_id=email.split("@")[0].upper()[:8],
        department=Department.ELECTRONICS,
    )
    db.add(student)
    db.commit()
    return user


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


def _current_student_id(db: Session, user: User) -> object:
    """Resolve the Student row id for a student user."""
    return db.scalar(select(Student).where(Student.user_id == user.id))


def _status_line(resp) -> str:
    """A short human description of a response for actual-output recording."""
    try:
        body = resp.json()
    except ValueError:
        body = resp.text or None
    return f"Status: {resp.status_code}, body: {body}"


# ------------------------------------------------------ POST /equipment
def test_create_equipment_duplicate_request(
    client: TestClient, club_admin: User, db_session: Session
) -> None:
    """Submitting the exact same create payload twice.

    Currently the API has no unique constraint on equipment, so a second
    identical create is expected to be rejected. The actual result is recorded
    as-is and is not corrected here.
    """
    payload = _valid_equipment_payload()

    response_one = client.post(
        f"{API}", json=payload, headers=auth_headers(club_admin)
    )
    response_two = client.post(
        f"{API}", json=payload, headers=auth_headers(club_admin)
    )
    record_actual(
        "first: " + _status_line(response_one) + ", second: " + _status_line(response_two)
    )

    assert response_one.status_code == 201
    assert response_two.status_code == 409


def test_create_equipment_success(
    client: TestClient, club_admin: User, db_session: Session
) -> None:
    payload = _valid_equipment_payload()

    response = client.post(f"{API}", json=payload, headers=auth_headers(club_admin))
    record_actual(_status_line(response))

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Oscilloscope"
    assert body["total_quantity"] == 10
    assert body["available_quantity"] == 10


def test_create_equipment_invalid_available_exceeds_total(
    client: TestClient, club_admin: User
) -> None:
    payload = _valid_equipment_payload(total_quantity=5, available_quantity=6)

    response = client.post(f"{API}", json=payload, headers=auth_headers(club_admin))
    record_actual(_status_line(response))

    assert response.status_code == 422


def test_create_equipment_total_quantity_validation(
    client: TestClient, club_admin: User
) -> None:
    payload = _valid_equipment_payload(total_quantity=0)

    response = client.post(f"{API}", json=payload, headers=auth_headers(club_admin))
    record_actual(_status_line(response))

    assert response.status_code == 422


def test_create_equipment_empty_name(client: TestClient, club_admin: User) -> None:
    payload = _valid_equipment_payload(name="")

    response = client.post(f"{API}", json=payload, headers=auth_headers(club_admin))
    record_actual(_status_line(response))

    assert response.status_code == 422


def test_create_equipment_rejects_extra_field(
    client: TestClient, club_admin: User
) -> None:
    payload = _valid_equipment_payload(unexpected_field_="boom")

    response = client.post(f"{API}", json=payload, headers=auth_headers(club_admin))
    record_actual(_status_line(response))

    assert response.status_code == 422


def test_create_equipment_student_forbidden(
    client: TestClient, student: User
) -> None:
    response = client.post(
        f"{API}", json=_valid_equipment_payload(), headers=auth_headers(student)
    )
    record_actual(_status_line(response))

    assert response.status_code == 403


def test_create_equipment_unauthenticated(client: TestClient) -> None:
    response = client.post(f"{API}", json=_valid_equipment_payload())
    record_actual(_status_line(response))

    assert response.status_code == 401


# ---------------------------------------- POST /equipment/stock/increase
def test_increase_equipment_stock_success(
    client: TestClient, club_admin: User, db_session: Session
) -> None:
    equipment = _create_equipment_in_db(db_session)

    payload = {"equipment_id": str(equipment.id), "increment_quantity": 5}
    response = client.post(
        f"{API}/stock/increase", json=payload, headers=auth_headers(club_admin)
    )
    record_actual(_status_line(response))

    assert response.status_code == 200
    body = response.json()
    assert body["total_quantity"] == 15
    assert body["available_quantity"] == 15


def test_increase_equipment_stock_not_found(
    client: TestClient, club_admin: User
) -> None:
    payload = {"equipment_id": str(uuid4()), "increment_quantity": 5}
    response = client.post(
        f"{API}/stock/increase", json=payload, headers=auth_headers(club_admin)
    )
    record_actual(_status_line(response))

    assert response.status_code == 404


def test_increase_equipment_stock_zero_increment(
    client: TestClient, club_admin: User, db_session: Session
) -> None:
    equipment = _create_equipment_in_db(db_session)

    payload = {"equipment_id": str(equipment.id), "increment_quantity": 0}
    response = client.post(
        f"{API}/stock/increase", json=payload, headers=auth_headers(club_admin)
    )
    record_actual(_status_line(response))

    assert response.status_code == 422


def test_increase_equipment_stock_student_forbidden(
    client: TestClient, student: User, db_session: Session
) -> None:
    equipment = _create_equipment_in_db(db_session)

    payload = {"equipment_id": str(equipment.id), "increment_quantity": 5}
    response = client.post(
        f"{API}/stock/increase", json=payload, headers=auth_headers(student)
    )
    record_actual(_status_line(response))

    assert response.status_code == 403


def test_increase_equipment_stock_unauthenticated(
    client: TestClient, db_session: Session
) -> None:
    equipment = _create_equipment_in_db(db_session)

    payload = {"equipment_id": str(equipment.id), "increment_quantity": 5}
    response = client.post(f"{API}/stock/increase", json=payload)
    record_actual(_status_line(response))

    assert response.status_code == 401


# ----------------------------------------------- POST /equipment/borrow
def test_borrow_equipment_new_borrow_created(
    client: TestClient, db_session: Session
) -> None:
    user = _user_with_profile(db_session, email="student@example.com")
    equipment = _create_equipment_in_db(db_session)

    response = client.post(
        f"{API}/borrow",
        json=_borrow_payload(str(equipment.id)),
        headers=auth_headers(user),
    )
    record_actual(_status_line(response))

    assert response.status_code == 201
    body = response.json()
    assert body["equipment_id"] == str(equipment.id)
    assert body["borrowed_quantity"] == 2
    assert body["student_email"] == "student@example.com"


def test_borrow_equipment_existing_borrow_updated(
    client: TestClient, db_session: Session
) -> None:
    user = _user_with_profile(db_session, email="student2@example.com")
    equipment = _create_equipment_in_db(db_session)

    first = _borrow_payload(str(equipment.id), borrowed_quantity=2)
    response_one = client.post(
        f"{API}/borrow", json=first, headers=auth_headers(user)
    )
    record_actual("first borrow: " + _status_line(response_one))
    assert response_one.status_code == 201

    second = _borrow_payload(str(equipment.id), borrowed_quantity=3)
    response_two = client.post(
        f"{API}/borrow", json=second, headers=auth_headers(user)
    )
    record_actual("second borrow: " + _status_line(response_two))

    assert response_two.status_code == 200
    assert response_two.json()["borrowed_quantity"] == 5


def test_borrow_equipment_exceeds_available_stock(
    client: TestClient, db_session: Session
) -> None:
    user = _user_with_profile(db_session, email="student3@example.com")
    equipment = _create_equipment_in_db(db_session)
    equipment.available_quantity = 1
    db_session.commit()

    response = client.post(
        f"{API}/borrow",
        json=_borrow_payload(str(equipment.id), borrowed_quantity=5),
        headers=auth_headers(user),
    )
    record_actual(_status_line(response))

    assert response.status_code == 400
    assert response.json()["detail"] == "Requested quantity exceeds available stock."


def test_borrow_equipment_not_found(client: TestClient, db_session: Session) -> None:
    user = _user_with_profile(db_session, email="student4@example.com")

    response = client.post(
        f"{API}/borrow",
        json=_borrow_payload(str(uuid4())),
        headers=auth_headers(user),
    )
    record_actual(_status_line(response))

    assert response.status_code == 404


def test_borrow_equipment_zero_quantity(
    client: TestClient, db_session: Session
) -> None:
    user = _user_with_profile(db_session, email="student5@example.com")
    equipment = _create_equipment_in_db(db_session)

    response = client.post(
        f"{API}/borrow",
        json=_borrow_payload(str(equipment.id), borrowed_quantity=0),
        headers=auth_headers(user),
    )
    record_actual(_status_line(response))

    assert response.status_code == 422


def test_borrow_equipment_admin_forbidden(
    client: TestClient, club_admin: User, db_session: Session
) -> None:
    equipment = _create_equipment_in_db(db_session)

    response = client.post(
        f"{API}/borrow",
        json=_borrow_payload(str(equipment.id)),
        headers=auth_headers(club_admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 403


def test_borrow_equipment_unauthenticated(client: TestClient) -> None:
    response = client.post(f"{API}/borrow", json=_borrow_payload(str(uuid4())))
    record_actual(_status_line(response))

    assert response.status_code == 401


# ------------------------------------------ DELETE /borrow-details/{id}
def test_delete_borrow_detail_restores_stock(
    client: TestClient, db_session: Session
) -> None:
    admin = _admin(db_session, email="admin@example.com")
    user = _user_with_profile(db_session, email="student6@example.com")
    equipment = _create_equipment_in_db(db_session)
    student_id = _current_student_id(db_session, user)

    borrow = BorrowDetail(
        equipment_id=equipment.id,
        student_id=student_id.id,
        borrowed_quantity=2,
        requested_date=datetime.now(UTC),
        return_date=datetime(2026, 12, 1, tzinfo=UTC),
    )
    db_session.add(borrow)
    db_session.commit()
    db_session.refresh(borrow)
    equipment.available_quantity = 8
    db_session.commit()

    response = client.delete(
        f"/api/borrow-details/{borrow.id}", headers=auth_headers(admin)
    )
    record_actual(_status_line(response))

    assert response.status_code == 204

    equipment_after = db_session.scalar(
        select(Equipment).where(Equipment.id == equipment.id)
    )
    record_actual(
        "Status: 204, available_quantity after delete: "
        + str(equipment_after.available_quantity if equipment_after else None)
    )
    assert equipment_after is not None
    assert equipment_after.available_quantity == 10


def test_delete_borrow_detail_not_found(
    client: TestClient, club_admin: User
) -> None:
    response = client.delete(
        f"/api/borrow-details/{uuid4()}", headers=auth_headers(club_admin)
    )
    record_actual(_status_line(response))

    assert response.status_code == 404


def test_delete_borrow_detail_student_forbidden(
    client: TestClient, student: User, db_session: Session
) -> None:
    user = _user_with_profile(db_session, email="student7@example.com")
    equipment = _create_equipment_in_db(db_session)
    student_id = _current_student_id(db_session, user)

    borrow = BorrowDetail(
        equipment_id=equipment.id,
        student_id=student_id.id,
        borrowed_quantity=1,
        requested_date=datetime.now(UTC),
        return_date=datetime(2026, 12, 1, tzinfo=UTC),
    )
    db_session.add(borrow)
    db_session.commit()
    db_session.refresh(borrow)

    response = client.delete(
        f"/api/borrow-details/{borrow.id}", headers=auth_headers(student)
    )
    record_actual(_status_line(response))

    assert response.status_code == 403


def test_delete_borrow_detail_unauthenticated(
    client: TestClient, db_session: Session
) -> None:
    user = _user_with_profile(db_session, email="student8@example.com")
    equipment = _create_equipment_in_db(db_session)
    student_id = _current_student_id(db_session, user)

    borrow = BorrowDetail(
        equipment_id=equipment.id,
        student_id=student_id.id,
        borrowed_quantity=1,
        requested_date=datetime.now(UTC),
        return_date=datetime(2026, 12, 1, tzinfo=UTC),
    )
    db_session.add(borrow)
    db_session.commit()
    db_session.refresh(borrow)

    response = client.delete(f"/api/borrow-details/{borrow.id}")
    record_actual(_status_line(response))

    assert response.status_code == 401