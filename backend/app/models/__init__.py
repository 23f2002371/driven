"""SQLAlchemy models package.

Import models here so Alembic autogenerate can discover them.
"""

from app.models.student import Student
from app.models.user import User

__all__ = ["Student", "User"]
