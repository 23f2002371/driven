"""Pydantic schemas for the Support Desk (event discussion forum) domain."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.utils.enums import UserRole


# ------------------------------------------------------------- Discussion
class DiscussionThreadCreate(BaseModel):
    """Payload to create the discussion thread for an event."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)


class DiscussionThreadResponse(BaseModel):
    """Representation of a discussion thread.

    ``creator_name`` is resolved from the related user and is therefore built
    by a helper rather than loaded directly from the thread row.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event_id: UUID
    title: str
    created_by: UUID
    creator_name: str
    created_at: datetime
    updated_at: datetime


class DiscussionMessageCreate(BaseModel):
    """Payload to post a message (top-level or nested reply) in a thread."""

    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1)
    parent_message_id: UUID | None = None


class DiscussionMessageUpdate(BaseModel):
    """Payload to edit a message. Only the content may change."""

    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1)


class DiscussionMessageResponse(BaseModel):
    """Representation of a discussion message.

    ``author_name`` and ``author_role`` are resolved from the related user and
    are built by a helper. ``replies`` is recursive so the full tree is
    serialised without any client-side assembly.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None = None
    author_name: str
    author_role: UserRole
    message: str
    created_at: datetime
    updated_at: datetime
    replies: list[DiscussionMessageResponse] = []