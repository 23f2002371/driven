"""Integration tests for the event endpoints.

Each test is self-contained and creates its own data via the API or the
``db_session`` fixture, never relying on test execution order.
"""

from __future__ import annotations

from datetime import UTC, date, datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.user import User
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
        "cover_image_url": "https://example.com/cover.png",
        "agendas": [],
        "additional_info": [],
        "mentors": [],
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


# ---------------------------------------------------------------- POST /events
def test_create_event_as_club_admin(
    client: TestClient, club_admin: User
) -> None:
    response = client.post(
        f"{API}",
        json=_valid_event_payload(),
        headers=auth_headers(club_admin),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Intro to AI Workshop"
    assert body["status"] == "pending"


def test_create_event_as_student_forbidden(client: TestClient, student: User) -> None:
    response = client.post(
        f"{API}",
        json=_valid_event_payload(),
        headers=auth_headers(student),
    )

    assert response.status_code == 403


def test_create_event_invalid_payload(client: TestClient, club_admin: User) -> None:
    response = client.post(
        f"{API}",
        json=_valid_event_payload(max_participants=0),
        headers=auth_headers(club_admin),
    )

    assert response.status_code == 422


def test_create_event_missing_required_field(
    client: TestClient, club_admin: User
) -> None:
    payload = _valid_event_payload()
    del payload["description"]

    response = client.post(f"{API}", json=payload, headers=auth_headers(club_admin))

    assert response.status_code == 422


def test_create_event_unauthenticated(client: TestClient) -> None:
    response = client.post(f"{API}", json=_valid_event_payload())

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
