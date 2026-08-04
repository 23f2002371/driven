"""SQLAlchemy models package.

Import models here so Alembic autogenerate can discover them.
"""

from app.models.event import (
    AdditionalEventInfo,
    Event,
    EventAgenda,
    EventMentor,
    EventRegistration,
    EventWinner,
)
from app.models.student import Student, StudentSkill
from app.models.user import User

__all__ = [
    "AdditionalEventInfo",
    "Event",
    "EventAgenda",
    "EventMentor",
    "EventRegistration",
    "EventWinner",
    "Student",
    "StudentSkill",
    "User",
]