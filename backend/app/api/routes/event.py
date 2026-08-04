"""Event endpoints.

- ``POST /events``                       - create an event (club/lab admin only).
- ``PATCH /events/{event_id}``           - update an event (club/lab admin only).
- ``GET  /events/{event_id}``            - fetch the public event page.
- ``GET  /events/{event_id}/private``    - fetch the full event for the admin dashboard.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import DbSession, get_current_user, require_roles
from app.models.event import AdditionalEventInfo, Event, EventAgenda, EventMentor
from app.models.user import User
from app.schemas.event import EventCreate, EventResponse, EventUpdate, PrivateEventResponse
from app.utils.enums import UserRole, WinnerPosition

router = APIRouter()

CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]

ClubAdmin = Annotated[
    User,
    Depends(require_roles(UserRole.CLUB_ADMIN))
]


@router.post(
    "/events",
    response_model=PrivateEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event(payload: EventCreate, db: DbSession, current_user: ClubAdmin) -> Event:
    """Create an event together with its agenda, additional info and mentors."""
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
def update_event(
    event_id: uuid.UUID,
    payload: EventUpdate,
    db: DbSession,
    current_user: ClubAdmin,
) -> Event:
    """Update an event, replacing any supplied child collections wholesale."""
    event = db.scalar(
        select(Event)
        .where(Event.id == event_id)
        .options(
            selectinload(Event.agendas),
            selectinload(Event.additional_info),
            selectinload(Event.mentors),
        )
    )
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    update_data = payload.model_dump(exclude_unset=True)
    agendas = update_data.pop("agendas", None)
    additional_info = update_data.pop("additional_info", None)
    mentors = update_data.pop("mentors", None)

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

        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update event",
        ) from exc
    db.refresh(event)
    return event


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
        )
    )
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    return event