"""Create slots table

Revision ID: ${TIMESTAMP}
Revises:
Create Date: $(date -u +"%Y-%m-%d %H:%M:%S")

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

# revision identifiers, used by Alembic.
revision = '${TIMESTAMP}'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create the slots table with appropriate constraints
    op.create_table(
        'slots',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('office_id', UUID(as_uuid=True), sa.ForeignKey('offices.id'), nullable=False),
        sa.Column('slot_date', sa.Date(), nullable=False),
        sa.Column('slot_time', sa.Time(), nullable=False),
        sa.Column('capacity', sa.SmallInteger(), nullable=False),
        sa.Column('taken', sa.SmallInteger(), nullable=False, server_default='0'),
        sa.CheckConstraint("slot_time >= '08:00:00'::time AND slot_time <= '17:00:00'::time",
                           name='check_slot_time_in_working_hours'),
        sa.CheckConstraint("EXTRACT(MINUTE FROM slot_time) IN (0, 30)",
                           name='check_slot_time_interval'),
        sa.CheckConstraint("taken <= capacity",
                           name='check_taken_lte_capacity')
    )

    # Create index for common query patterns
    op.create_index('ix_slots_office_id_date', 'slots', ['office_id', 'slot_date'])

def downgrade() -> None:
    op.drop_table('slots')
