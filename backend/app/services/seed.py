"""Seed script for administrative accounts.

Run after applying migrations to provision the two internal admin roles::

    uv run python -m app.services.seed

Both accounts are created with placeholder emails and a documented placeholder
password. Change the credentials before the platform goes live.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.utils.enums import UserRole


@dataclass(frozen=True)
class AdminAccount:

    full_name: str
    email: str
    role: UserRole



ADMIN_SEED_PASSWORD = "navanit"
ADMIN_SEED_ACCOUNTS: tuple[AdminAccount, ...] = (
    AdminAccount(
        full_name="Navanit ray",
        email="navneetrai456@gmail.com",
        role=UserRole.CLUB_ADMIN,
    ),
    AdminAccount(
        full_name="23F3003186Nav",
        email="23f3003186@ds.study.iitm.ac.in",
        role=UserRole.LAB_ADMIN,
    ),
)


def seed_admin_accounts(db: Session) -> int:
    
    """Create the admin accounts if they do not exist yet.
    Returns the number of accounts created in this run.
    """
    created = 0
    for account in ADMIN_SEED_ACCOUNTS:
        exists = db.scalar(select(User).where(User.email == account.email))
        if exists is not None:
            continue
        db.add(
            User(
                full_name=account.full_name,
                email=account.email,
                password_hash=get_password_hash(ADMIN_SEED_PASSWORD),
                role=account.role,
            )
        )
        created += 1
    db.commit()
    return created


if __name__ == "__main__":
    with SessionLocal() as session:
        count = seed_admin_accounts(session)
        print(f"Seeded {count} admin account(s).")
        for account in ADMIN_SEED_ACCOUNTS:
            print(f"  {account.role.value:<12} {account.email}")
