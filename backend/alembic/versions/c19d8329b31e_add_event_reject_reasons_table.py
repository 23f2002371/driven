"""Add event_reject_reasons table and event_rejection_reason enum

Revision ID: c19d8329b31e
Revises: b48f60142cf2
Create Date: 2026-08-23 11:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c19d8329b31e'
down_revision: Union[str, None] = 'a48fe1f62e9c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    event_rejection_reason = postgresql.ENUM(
        'venue_not_available',
        'time_slot_conflict',
        'equipment_not_available',
        'capacity_exceeded',
        'incomplete_information',
        'other',
        name='event_rejection_reason',
        create_type=False,
    )
    event_rejection_reason.create(op.get_bind(), checkfirst=True)

    event_venue = postgresql.ENUM(
        'seminar_hall',
        'auditorium',
        'main_ground',
        'computer_lab_1',
        'computer_lab_2',
        'robotics_lab',
        'innovation_lab',
        'conference_room',
        'classroom',
        'online',
        'other',
        name='event_venue',
        create_type=False,
    )

    op.create_table(
        'event_reject_reasons',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('event_id', sa.Uuid(), nullable=False),
        sa.Column('reason', event_rejection_reason, nullable=False),
        sa.Column('alternative_venue', event_venue, nullable=True),
        sa.Column('alternative_date', sa.Date(), nullable=True),
        sa.Column('admin_comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id'),
    )
    op.create_index(op.f('ix_event_reject_reasons_event_id'), 'event_reject_reasons', ['event_id'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_event_reject_reasons_event_id'), table_name='event_reject_reasons')
    op.drop_table('event_reject_reasons')
    postgresql.ENUM(name='event_rejection_reason').drop(op.get_bind(), checkfirst=True)
