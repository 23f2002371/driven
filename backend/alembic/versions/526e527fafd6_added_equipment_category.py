"""added equipment category

Revision ID: 526e527fafd6
Revises: 12d11e36c9a6
Create Date: 2026-08-23 15:43:49.846624

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '526e527fafd6'
down_revision: Union[str, None] = '12d11e36c9a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define the PostgreSQL Enum type
equipment_category_enum = postgresql.ENUM(
    'electronics',
    'microcontroller',
    'sensor_module',
    'robotics',
    'audio_visual',
    'computing_hardware',
    'networking',
    'tools_and_hardware',
    'other',
    name='equipment_category',
)


def upgrade() -> None:
    # 1. Create the enum type in PostgreSQL
    equipment_category_enum.create(op.get_bind(), checkfirst=True)

    # 2. Alter the column with postgresql_using cast
    op.alter_column(
        'equipment',
        'category',
        existing_type=sa.VARCHAR(length=100),
        type_=equipment_category_enum,
        existing_nullable=False,
        postgresql_using="category::text::equipment_category",
    )


def downgrade() -> None:
    # 1. Revert column back to VARCHAR
    op.alter_column(
        'equipment',
        'category',
        existing_type=equipment_category_enum,
        type_=sa.VARCHAR(length=100),
        existing_nullable=False,
    )

    # 2. Drop the enum type
    equipment_category_enum.drop(op.get_bind(), checkfirst=True)
