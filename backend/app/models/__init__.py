"""SQLAlchemy models package.

Import models here so Alembic autogenerate can discover them.
"""

from app.models.bounty import (
    Application,
    Bounty,
    BountyTechnology,
    Deliverable,
    Responsibility,
    Work,
)
from app.models.domain import Domain, StudentDomain, StudentTechnology, Technology
from app.models.event import (
    AdditionalEventInfo,
    Event,
    EventAgenda,
    EventMentor,
    EventRegistration,
    EventWinner,
)
from app.models.inventory import BorrowDetail, Equipment
from app.models.student import Student
from app.models.support_desk import DiscussionMessage, DiscussionThread
from app.models.user import User

__all__ = [
    "AdditionalEventInfo",
    "Application",
    "BorrowDetail",
    "Bounty",
    "BountyTechnology",
    "Deliverable",
    "DiscussionMessage",
    "DiscussionThread",
    "Domain",
    "Equipment",
    "Event",
    "EventAgenda",
    "EventMentor",
    "EventRegistration",
    "EventWinner",
    "Responsibility",
    "Student",
    "StudentDomain",
    "StudentTechnology",
    "Technology",
    "User",
    "Work",
]