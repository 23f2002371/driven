"""Application enums.

Enums are defined here so they can be shared between the SQLAlchemy models
(database layer) and the Pydantic schemas (API layer).

Each enum subclasses ``str`` so that serialized values match the PostgreSQL
enum values exactly.
"""

from enum import Enum


class UserRole(str, Enum):
    """Role assigned to a user.

    Only ``STUDENT`` is reachable through the public API. The administrative
    roles are created internally via seeding or future admin tooling.
    """

    STUDENT = "student"
    CLUB_ADMIN = "club_admin"
    LAB_ADMIN = "lab_admin"
