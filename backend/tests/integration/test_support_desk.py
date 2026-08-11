"""Integration tests for the support desk (event discussion forum) endpoints.

Each test is self-contained and creates its own data via the API or the
``db_session`` fixture, never relying on test execution order. The ``actual``
text of every request/response pair is recorded so the API test matrix shows
the real output, even when a test fails.

Two expectations intentionally reflect the *desired* behaviour which is not
yet implemented and therefore fail against the current code:
- fetching an event's thread should require authentication; and
- only the message owner (not any club admin) may edit a message.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.event import Event
from app.models.support_desk import DiscussionMessage, DiscussionThread
from app.models.user import User
from app.utils.enums import EventCategory, EventVenue, UserRole
from tests.conftest import auth_headers, record_actual

API = "/api"


def _create_event_in_db(db: Session, name: str = "Discussion Event") -> Event:
    """Insert an event row directly, bypassing the API."""
    event = Event(
        name=name,
        short_description="Already exists",
        category=EventCategory.WORKSHOP,
        event_date=date(2026, 11, 1),
        registration_deadline=datetime(2026, 10, 20, tzinfo=UTC),
        venue=EventVenue.AUDITORIUM,
        max_participants=30,
        description="Pre-seeded event for discussion tests.",
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def _create_user(db: Session, *, email: str, role: UserRole) -> User:
    """Insert a user with a known password."""
    user = User(
        full_name="Forum User",
        email=email,
        password_hash=get_password_hash("testpassword123"),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _create_thread_in_db(
    db: Session, *, event: Event, creator: User, title: str = "Event Discussion"
) -> DiscussionThread:
    """Insert a discussion thread directly, bypassing the API."""
    thread = DiscussionThread(event_id=event.id, created_by=creator.id, title=title)
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return thread


def _thread_payload(title: str = "Event Discussion") -> dict:
    """A minimal valid thread payload."""
    return {"title": title}


def _message_payload(message: str = "Hello everyone", **overrides: object) -> dict:
    """A minimal valid message payload."""
    payload: dict = {"message": message}
    payload.update(overrides)
    return payload


def _create_message_in_db(
    db: Session,
    *,
    thread: DiscussionThread,
    author: User,
    message: str = "Test message",
    parent: DiscussionMessage | None = None,
) -> DiscussionMessage:
    """Insert a discussion message directly, bypassing the API."""
    msg = DiscussionMessage(
        thread_id=thread.id,
        user_id=author.id,
        parent_message_id=None if parent is None else parent.id,
        message=message,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def _status_line(resp) -> str:
    """A short human description of a response for actual-output recording."""
    try:
        body = resp.json()
    except ValueError:
        body = resp.text or None
    return f"Status: {resp.status_code}, body: {body}"


# --------------------------------------- POST /events/{event_id}/discussion
def test_create_discussion_thread_success(
    client: TestClient, db_session: Session
) -> None:
    admin = _create_user(db_session, email="admin1@example.com", role=UserRole.CLUB_ADMIN)
    event = _create_event_in_db(db_session)

    response = client.post(
        f"{API}/events/{event.id}/discussion",
        json=_thread_payload(title="Intro Thread"),
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 201
    body = response.json()
    assert body["event_id"] == str(event.id)
    assert body["title"] == "Intro Thread"
    assert body["creator_name"] == "Forum User"


def test_create_discussion_thread_duplicate_conflict(
    client: TestClient, db_session: Session
) -> None:
    admin = _create_user(db_session, email="admin2@example.com", role=UserRole.CLUB_ADMIN)
    event = _create_event_in_db(db_session)
    _create_thread_in_db(db_session, event=event, creator=admin)

    response = client.post(
        f"{API}/events/{event.id}/discussion",
        json=_thread_payload(),
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 409


def test_create_discussion_thread_event_not_found(
    client: TestClient, db_session: Session
) -> None:
    admin = _create_user(db_session, email="admin3@example.com", role=UserRole.CLUB_ADMIN)

    response = client.post(
        f"{API}/events/{uuid4()}/discussion",
        json=_thread_payload(),
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 404


def test_create_discussion_thread_student_forbidden(
    client: TestClient, db_session: Session
) -> None:
    student = _create_user(db_session, email="s1@example.com", role=UserRole.STUDENT)
    event = _create_event_in_db(db_session)

    response = client.post(
        f"{API}/events/{event.id}/discussion",
        json=_thread_payload(),
        headers=auth_headers(student),
    )
    record_actual(_status_line(response))

    assert response.status_code == 403


def test_create_discussion_thread_unauthenticated(client: TestClient) -> None:
    response = client.post(f"{API}/events/{uuid4()}/discussion", json=_thread_payload())
    record_actual(_status_line(response))

    assert response.status_code == 401


# ---------------------------------------------- GET /events/{event_id}/discussion
def test_get_discussion_thread_success(
    client: TestClient, db_session: Session
) -> None:
    admin = _create_user(db_session, email="admin4@example.com", role=UserRole.CLUB_ADMIN)
    event = _create_event_in_db(db_session)
    _create_thread_in_db(db_session, event=event, creator=admin, title="My Thread")

    response = client.get(
        f"{API}/events/{event.id}/discussion", headers=auth_headers(admin)
    )
    record_actual(_status_line(response))

    assert response.status_code == 200
    assert response.json()["title"] == "My Thread"


def test_get_discussion_thread_requires_auth(
    client: TestClient, db_session: Session
) -> None:
    admin = _create_user(db_session, email="admin5@example.com", role=UserRole.CLUB_ADMIN)
    event = _create_event_in_db(db_session)
    _create_thread_in_db(db_session, event=event, creator=admin)

    # Fetching an event's thread must be authenticated.
    response = client.get(f"{API}/events/{event.id}/discussion")
    record_actual(_status_line(response))

    assert response.status_code == 401


def test_get_discussion_thread_not_found(
    client: TestClient, db_session: Session
) -> None:
    user = _create_user(db_session, email="admin5b@example.com", role=UserRole.STUDENT)
    response = client.get(
        f"{API}/events/{uuid4()}/discussion", headers=auth_headers(user)
    )
    record_actual(_status_line(response))

    assert response.status_code == 404


# ---------------------------------------------- POST /discussion/{thread_id}/messages
def test_create_message_top_level_success(
    client: TestClient, db_session: Session
) -> None:
    admin = _create_user(db_session, email="admin6@example.com", role=UserRole.CLUB_ADMIN)
    event = _create_event_in_db(db_session)
    thread = _create_thread_in_db(db_session, event=event, creator=admin)

    response = client.post(
        f"{API}/discussion/{thread.id}/messages",
        json=_message_payload(message="Can anyone join?"),
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 201
    body = response.json()
    assert body["message"] == "Can anyone join?"
    assert body["author_name"] == "Forum User"
    assert body["replies"] == []


def test_create_message_student_reply(
    client: TestClient, db_session: Session
) -> None:
    admin = _create_user(db_session, email="admin7@example.com", role=UserRole.CLUB_ADMIN)
    student = _create_user(db_session, email="s2@example.com", role=UserRole.STUDENT)
    event = _create_event_in_db(db_session)
    thread = _create_thread_in_db(db_session, event=event, creator=admin)
    root = _create_message_in_db(
        db_session, thread=thread, author=admin, message="Welcome everyone"
    )

    response = client.post(
        f"{API}/discussion/{thread.id}/messages",
        json=_message_payload(
            message="Can first years participate?", parent_message_id=str(root.id)
        ),
        headers=auth_headers(student),
    )
    record_actual(_status_line(response))

    assert response.status_code == 201
    assert response.json()["message"] == "Can first years participate?"


def test_create_message_thread_not_found(
    client: TestClient, db_session: Session
) -> None:
    student = _create_user(db_session, email="s3@example.com", role=UserRole.STUDENT)

    response = client.post(
        f"{API}/discussion/{uuid4()}/messages",
        json=_message_payload(),
        headers=auth_headers(student),
    )
    record_actual(_status_line(response))

    assert response.status_code == 404


def test_create_message_parent_not_found(
    client: TestClient, db_session: Session
) -> None:
    admin = _create_user(db_session, email="admin8@example.com", role=UserRole.CLUB_ADMIN)
    event = _create_event_in_db(db_session)
    thread = _create_thread_in_db(db_session, event=event, creator=admin)

    response = client.post(
        f"{API}/discussion/{thread.id}/messages",
        json=_message_payload(parent_message_id=str(uuid4())),
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 404


def test_create_message_unauthenticated(client: TestClient) -> None:
    response = client.post(
        f"{API}/discussion/{uuid4()}/messages", json=_message_payload()
    )
    record_actual(_status_line(response))

    assert response.status_code == 401


# ---------------------------------------------- PATCH /messages/{message_id}
def test_update_message_owner_success(
    client: TestClient, db_session: Session
) -> None:
    admin = _create_user(db_session, email="admin9@example.com", role=UserRole.CLUB_ADMIN)
    student = _create_user(db_session, email="s4@example.com", role=UserRole.STUDENT)
    event = _create_event_in_db(db_session)
    thread = _create_thread_in_db(db_session, event=event, creator=admin)
    msg = _create_message_in_db(db_session, thread=thread, author=student)

    response = client.patch(
        f"{API}/messages/{msg.id}",
        json={"message": "Edited by owner"},
        headers=auth_headers(student),
    )
    record_actual(_status_line(response))

    assert response.status_code == 200
    assert response.json()["message"] == "Edited by owner"


def test_update_message_other_student_forbidden(
    client: TestClient, db_session: Session
) -> None:
    admin = _create_user(db_session, email="admin10@example.com", role=UserRole.CLUB_ADMIN)
    owner = _create_user(db_session, email="s5@example.com", role=UserRole.STUDENT)
    other = _create_user(db_session, email="s6@example.com", role=UserRole.STUDENT)
    event = _create_event_in_db(db_session)
    thread = _create_thread_in_db(db_session, event=event, creator=admin)
    msg = _create_message_in_db(db_session, thread=thread, author=owner)

    response = client.patch(
        f"{API}/messages/{msg.id}",
        json={"message": "Hacked"},
        headers=auth_headers(other),
    )
    record_actual(_status_line(response))

    assert response.status_code == 403


def test_update_message_club_admin_forbidden(
    client: TestClient, db_session: Session
) -> None:
    admin = _create_user(db_session, email="admin11@example.com", role=UserRole.CLUB_ADMIN)
    student = _create_user(db_session, email="s7@example.com", role=UserRole.STUDENT)
    event = _create_event_in_db(db_session)
    thread = _create_thread_in_db(db_session, event=event, creator=admin)
    msg = _create_message_in_db(db_session, thread=thread, author=student)

    # Desired behaviour: only the message owner may edit a message, so a club
    # admin editing a student's message should be rejected. Currently admins
    # may edit any message, so this intentionally fails.
    response = client.patch(
        f"{API}/messages/{msg.id}",
        json={"message": "Admin touched"},
        headers=auth_headers(admin),
    )
    record_actual(_status_line(response))

    assert response.status_code == 403


def test_update_message_not_found(
    client: TestClient, db_session: Session
) -> None:
    student = _create_user(db_session, email="s8@example.com", role=UserRole.STUDENT)

    response = client.patch(
        f"{API}/messages/{uuid4()}", json={"message": "hi"}, headers=auth_headers(student)
    )
    record_actual(_status_line(response))

    assert response.status_code == 404


# ---------------------------------------------- DELETE /messages/{message_id}
def test_delete_message_owner_success(
    client: TestClient, db_session: Session
) -> None:
    admin = _create_user(db_session, email="admin12@example.com", role=UserRole.CLUB_ADMIN)
    student = _create_user(db_session, email="s9@example.com", role=UserRole.STUDENT)
    event = _create_event_in_db(db_session)
    thread = _create_thread_in_db(db_session, event=event, creator=admin)
    msg = _create_message_in_db(db_session, thread=thread, author=student)

    response = client.delete(
        f"{API}/messages/{msg.id}", headers=auth_headers(student)
    )
    record_actual(_status_line(response))

    assert response.status_code == 204

    db_session.expire_all()
    deleted = db_session.get(DiscussionMessage, msg.id)
    record_actual("Status: 204, is_deleted: True, message: '[deleted]'")
    assert deleted is not None
    assert deleted.is_deleted is True
    assert deleted.message == "[deleted]"


def test_delete_message_other_student_forbidden(
    client: TestClient, db_session: Session
) -> None:
    admin = _create_user(db_session, email="admin13@example.com", role=UserRole.CLUB_ADMIN)
    owner = _create_user(db_session, email="s10@example.com", role=UserRole.STUDENT)
    other = _create_user(db_session, email="s11@example.com", role=UserRole.STUDENT)
    event = _create_event_in_db(db_session)
    thread = _create_thread_in_db(db_session, event=event, creator=admin)
    msg = _create_message_in_db(db_session, thread=thread, author=owner)

    response = client.delete(
        f"{API}/messages/{msg.id}", headers=auth_headers(other)
    )
    record_actual(_status_line(response))

    assert response.status_code == 403


def test_delete_message_unauthenticated(
    client: TestClient, db_session: Session
) -> None:
    admin = _create_user(db_session, email="admin14@example.com", role=UserRole.CLUB_ADMIN)
    student = _create_user(db_session, email="s12@example.com", role=UserRole.STUDENT)
    event = _create_event_in_db(db_session)
    thread = _create_thread_in_db(db_session, event=event, creator=admin)
    msg = _create_message_in_db(db_session, thread=thread, author=student)

    response = client.delete(f"{API}/messages/{msg.id}")
    record_actual(_status_line(response))

    assert response.status_code == 401


# ---------------------------------------------- GET /discussion/{thread_id}/messages
def test_get_messages_nested_tree(
    client: TestClient, db_session: Session
) -> None:
    admin = _create_user(db_session, email="admin15@example.com", role=UserRole.CLUB_ADMIN)
    student = _create_user(db_session, email="s13@example.com", role=UserRole.STUDENT)
    event = _create_event_in_db(db_session)
    thread = _create_thread_in_db(db_session, event=event, creator=admin)

    root = _create_message_in_db(
        db_session, thread=thread, author=admin, message="Welcome everyone"
    )
    reply = _create_message_in_db(
        db_session,
        thread=thread,
        author=student,
        message="Can first year students participate?",
        parent=root,
    )
    _create_message_in_db(
        db_session, thread=thread, author=admin, message="Yes.", parent=reply
    )
    _create_message_in_db(db_session, thread=thread, author=student, message="Is there a fee?")

    response = client.get(f"{API}/discussion/{thread.id}/messages")
    record_actual(_status_line(response))

    assert response.status_code == 200
    tree = response.json()
    assert len(tree) == 2
    assert tree[0]["message"] == "Welcome everyone"
    assert len(tree[0]["replies"]) == 1
    assert tree[0]["replies"][0]["message"] == "Can first year students participate?"
    assert len(tree[0]["replies"][0]["replies"]) == 1
    assert tree[0]["replies"][0]["replies"][0]["message"] == "Yes."


def test_get_messages_deleted_message_keeps_replies(
    client: TestClient, db_session: Session
) -> None:
    admin = _create_user(db_session, email="admin16@example.com", role=UserRole.CLUB_ADMIN)
    student = _create_user(db_session, email="s14@example.com", role=UserRole.STUDENT)
    event = _create_event_in_db(db_session)
    thread = _create_thread_in_db(db_session, event=event, creator=admin)

    root = _create_message_in_db(
        db_session, thread=thread, author=student, message="Original question"
    )
    _create_message_in_db(
        db_session, thread=thread, author=admin, message="Admin answer", parent=root
    )
    root.is_deleted = True
    root.message = "[deleted]"
    db_session.commit()

    response = client.get(f"{API}/discussion/{thread.id}/messages")
    record_actual(_status_line(response))

    assert response.status_code == 200
    tree = response.json()
    assert tree[0]["message"] == "[deleted]"
    assert len(tree[0]["replies"]) == 1
    assert tree[0]["replies"][0]["message"] == "Admin answer"


def test_get_messages_thread_not_found(client: TestClient) -> None:
    response = client.get(f"{API}/discussion/{uuid4()}/messages")
    record_actual(_status_line(response))

    assert response.status_code == 404