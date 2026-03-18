from typing import Dict, Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
import logging

from app.models.user import User
from app.models.booking import Booking
from app.models.slot import Slot
from app.models.location import Location

logger = logging.getLogger("user_service")

async def get_user_data_export(db: Session, user_id: UUID) -> Dict:
    """
    Retrieve all user data for GDPR export

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        Dict containing user profile and booking history
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    # Get user profile data (excluding password)
    profile = {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "phone_number": user.phone_number,
        "created_at": user.created_at,
        "is_active": user.is_active
    }

    # Get all user bookings
    bookings_query = (
        db.query(
            Booking.id,
            Booking.slot_id,
            Slot.start_time,
            Slot.end_time,
            Location.name.label("location"),
            Booking.status,
            Booking.created_at
        )
        .join(Slot, Booking.slot_id == Slot.id)
        .join(Location, Slot.location_id == Location.id)
        .filter(Booking.user_id == user_id)
        .order_by(Slot.start_time.desc())
    )

    bookings = []
    for b in bookings_query.all():
        bookings.append({
            "id": b.id,
            "slot_id": b.slot_id,
            "start_time": b.start_time,
            "end_time": b.end_time,
            "location": b.location,
            "status": b.status,
            "created_at": b.created_at
        })

    return {"profile": profile, "bookings": bookings}

async def delete_user_account(db: Session, user_id: UUID) -> bool:
    """
    Delete a user account and all associated data

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        bool: True if deletion was successful
    """
    from app.services.email_service import EmailService

    try:
        # Get user information for email confirmation
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"Attempt to delete non-existent user: {user_id}")
            return False

        user_email = user.email
        user_name = user.full_name

        # Delete all associated bookings first (cascade delete)
        db.query(Booking).filter(Booking.user_id == user_id).delete()

        # Delete the user
        db.query(User).filter(User.id == user_id).delete()

        # Commit the changes
        db.commit()

        # Send confirmation email
        await EmailService.send_account_deletion_confirmation(user_email, user_name)

        logger.info(f"User account deleted: {user_id}")
        return True

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise
