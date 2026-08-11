"""Support desk (event discussion forum) endpoints.

- ``POST /events/{event_id}/discussion``        - create the thread for an event (club admin only).
- ``GET  /events/{event_id}/discussion``        - fetch an event's thread (authenticated).
- ``POST /discussion/{thread_id}/messages``     - post a message or nested reply (authenticated).
- ``PATCH /messages/{message_id}``              - edit a message (owner only).
- ``DELETE /messages/{message_id}``             - soft-delete a message (owner or club admin).
- ``GET  /discussion/{thread_id}/messages``     - fetch the whole discussion as a nested tree.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import DbSession, get_current_user, require_roles
from app.models.event import Event
from app.models.support_desk import DiscussionMessage, DiscussionThread
from app.models.user import User
from app.schemas.support_desk import (
    DiscussionMessageCreate,
    DiscussionMessageResponse,
    DiscussionMessageUpdate,
    DiscussionThreadCreate,
    DiscussionThreadResponse,
)
from app.utils.enums import UserRole

router = APIRouter()

CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]

ClubAdmin = Annotated[
    User,
    Depends(require_roles(UserRole.CLUB_ADMIN))
]


def _thread_response(thread: DiscussionThread) -> DiscussionThreadResponse:
    """Build the thread response, including the creator's name."""
    return DiscussionThreadResponse(
        id=thread.id,
        event_id=thread.event_id,
        title=thread.title,
        created_by=thread.created_by,
        creator_name=thread.creator.full_name,
        created_at=thread.created_at,
        updated_at=thread.updated_at,
    )


def _message_response(message: DiscussionMessage) -> DiscussionMessageResponse:
    """Build a single message response, including the author's details and its
    nested replies."""
    return DiscussionMessageResponse(
        id=message.id,
        author_name=message.user.full_name,
        author_role=message.user.role,
        message=message.message,
        created_at=message.created_at,
        updated_at=message.updated_at,
        replies=[
            _message_response(child) for child in sorted(message.children, key=lambda m: m.created_at)
        ],
    )


def _message_tree(messages: list[DiscussionMessage]) -> list[DiscussionMessageResponse]:
    """Assemble top-level messages with their nested reply trees."""
    return [_message_response(message) for message in messages]


# ----------------------------------------------------------- Thread
@router.post(
    "/events/{event_id}/discussion",
    response_model=DiscussionThreadResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_discussion_thread(
    event_id: uuid.UUID,
    payload: DiscussionThreadCreate,
    db: DbSession,
    current_user: ClubAdmin,
) -> DiscussionThreadResponse:
    """Create the single discussion thread for an event (club admin only).

    The event must exist and must not already have a discussion thread;
    otherwise a 409 conflict is raised.
    """
    event = db.scalar(select(Event).where(Event.id == event_id))
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    existing = db.scalar(
        select(DiscussionThread).where(DiscussionThread.event_id == event_id)
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Discussion already exists for this event",
        )

    thread = DiscussionThread(
        event_id=event_id,
        created_by=current_user.id,
        title=payload.title,
    )
    db.add(thread)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create discussion thread",
        ) from exc
    db.refresh(thread)
    return _thread_response(thread)


@router.get(
    "/events/{event_id}/discussion",
    response_model=DiscussionThreadResponse,
)
def get_event_discussion_thread(
    event_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> DiscussionThreadResponse:
    """Fetch the discussion thread belonging to an event (authentication
    required)."""
    thread = db.scalar(
        select(DiscussionThread)
        .where(DiscussionThread.event_id == event_id)
        .options(selectinload(DiscussionThread.creator))
    )
    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found",
        )
    return _thread_response(thread)


# ----------------------------------------------------------- Messages
@router.post(
    "/discussion/{thread_id}/messages",
    response_model=DiscussionMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_discussion_message(
    thread_id: uuid.UUID,
    payload: DiscussionMessageCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> DiscussionMessageResponse:
    """Post a message in a discussion thread (any authenticated user).

    When ``parent_message_id`` is omitted the message is a top-level post;
    when supplied it is stored as a reply to that message.
    """
    thread = db.scalar(select(DiscussionThread).where(DiscussionThread.id == thread_id))
    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found",
        )

    parent = None
    if payload.parent_message_id is not None:
        parent = db.scalar(
            select(DiscussionMessage).where(
                DiscussionMessage.id == payload.parent_message_id
            )
        )
        if parent is None or parent.thread_id != thread_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent message not found",
            )

    message = DiscussionMessage(
        thread_id=thread_id,
        user_id=current_user.id,
        parent_message_id=payload.parent_message_id,
        message=payload.message,
    )
    db.add(message)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to post message",
        ) from exc
    db.refresh(message)
    return _message_response(message)


@router.patch(
    "/messages/{message_id}",
    response_model=DiscussionMessageResponse,
)
def update_discussion_message(
    message_id: uuid.UUID,
    payload: DiscussionMessageUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> DiscussionMessageResponse:
    """Edit a message. Only the owner may change the content."""
    message = _get_message_or_404(db, message_id)

    if message.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to edit this message",
        )

    message.message = payload.message
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update message",
        ) from exc
    db.refresh(message)
    return _message_response(message)


@router.delete(
    "/messages/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_discussion_message(
    message_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Soft-delete a discussion message (owner or club admin).

    The row is kept so replies stay attached; ``is_deleted`` is set and the
    content is replaced with ``[deleted]``.
    """
    message = _get_message_or_404(db, message_id)

    if message.user_id != current_user.id and current_user.role != UserRole.CLUB_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete this message",
        )

    message.is_deleted = True
    message.message = "[deleted]"
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete message",
        ) from exc


@router.get(
    "/discussion/{thread_id}/messages",
    response_model=list[DiscussionMessageResponse],
)
def get_discussion_messages(
    thread_id: uuid.UUID,
    db: DbSession,
) -> list[DiscussionMessageResponse]:
    """Fetch the entire discussion as a nested reply tree (no authentication
    required).

    Only top-level messages are returned; each message embeds its replies
    recursively so the frontend renders the hierarchy directly.
    """
    thread = db.scalar(select(DiscussionThread).where(DiscussionThread.id == thread_id))
    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found",
        )

    messages = list(
        db.scalars(
            select(DiscussionMessage)
            .where(DiscussionMessage.thread_id == thread_id)
            .options(
                selectinload(DiscussionMessage.user),
                selectinload(DiscussionMessage.children),
            )
            .order_by(DiscussionMessage.created_at)
        )
    )
    top_level = [message for message in messages if message.parent_message_id is None]
    return _message_tree(top_level)


def _get_message_or_404(db: DbSession, message_id: uuid.UUID) -> DiscussionMessage:
    """Fetch a message row or raise 404."""
    message = db.scalar(
        select(DiscussionMessage)
        .where(DiscussionMessage.id == message_id)
        .options(selectinload(DiscussionMessage.user))
    )
    if message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )
    return message
