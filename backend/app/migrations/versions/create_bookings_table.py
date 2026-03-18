"""create bookings table

Revision ID: 20240501145100
Revises:
Create Date: 2024-05-01 14:51:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

# revision identifiers, used by Alembic.
revision = '20240501145100'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'bookings',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('slot_id', UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('booked_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),

        # Constraints
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['slot_id'], ['slots.id'], ondelete='CASCADE'),
        sa.CheckConstraint("status IN ('confirmed', 'cancelled')", name='valid_status_check'),
    )

    # Create an index for performance on common lookups
    op.create_index('idx_bookings_user_id', 'bookings', ['user_id'])
    op.create_index('idx_bookings_slot_id', 'bookings', ['slot_id'])
    op.create_index('idx_bookings_status', 'bookings', ['status'])

    # Create a unique constraint to prevent duplicate bookings (user can book a slot only once)
    op.create_index('idx_unique_user_slot', 'bookings', ['user_id', 'slot_id'], unique=True)

def downgrade():
    op.drop_table('bookings')
