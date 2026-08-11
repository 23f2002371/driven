"""Support desk models.

Event discussion forum: one ``DiscussionThread`` per event with nested
``DiscussionMessage`` records. Replies are threaded as a self-referencing
child/parent tree.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.event import Event
    from app.models.user import User


class DiscussionThread(Base):
    """The single discussion thread belonging to an event."""

    __tablename__ = "discussion_threads"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    event: Mapped[Event] = relationship("Event", back_populates="discussion_thread")
    creator: Mapped[User] = relationship(
        "User",
        back_populates="discussion_threads_created",
    )
    messages: Mapped[list[DiscussionMessage]] = relationship(
        "DiscussionMessage",
        back_populates="thread",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<DiscussionThread id={self.id} event_id={self.event_id} "
            f"title={self.title!r}>"
        )


class DiscussionMessage(Base):
    """A single message (top-level post or reply) in a discussion thread."""

    __tablename__ = "discussion_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    thread_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("discussion_threads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parent_message_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("discussion_messages.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    )

    thread: Mapped[DiscussionThread] = relationship(
        "DiscussionThread",
        back_populates="messages",
    )
    user: Mapped[User] = relationship("User", back_populates="discussion_messages")
    parent: Mapped[DiscussionMessage | None] = relationship(
        "DiscussionMessage",
        back_populates="children",
        remote_side=[id],
    )
    children: Mapped[list[DiscussionMessage]] = relationship(
        "DiscussionMessage",
        back_populates="parent",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<DiscussionMessage id={self.id} thread_id={self.thread_id} "
            f"user_id={self.user_id} parent_message_id={self.parent_message_id}>"
        )