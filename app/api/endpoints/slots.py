from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user
from app.schemas.slot import SlotReservationRequest, SlotReservationResponse
from app.repositories.slot_repository import SlotRepository
from app.db.session import get_db
from app.models.user import User
from app.core.logging import log_activity
from app.middlewares.rate_limiter import RateLimiter
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Apply rate limiting to prevent abuse
rate_limiter = RateLimiter(requests_limit=5, window_seconds=60)  # 5 requests per minute

@router.post("/reserve", response_model=SlotReservationResponse)
async def reserve_slot(
    request: Request,
    reservation: SlotReservationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(rate_limiter)
):
    """
    Reserve a slot for the authenticated user.

    This endpoint:
    1. Validates the slot is available
    2. Creates a reservation with transaction handling
    3. Logs the activity for audit purposes
    4. Returns the reservation details

    Rate limited to 5 requests per minute per IP address.
    """
    try:
        # Log the attempt for security audit
        logger.info(f"User {current_user.id} attempting to reserve slot {reservation.slot_id}")

        # Create repository for database operations
        slot_repo = SlotRepository(db)

        # Check if slot is available (will raise HTTPException if not)
        await slot_repo.get_available_slot(
            slot_id=reservation.slot_id,
            reservation_date=reservation.reservation_date
        )

        # Reserve the slot with transaction handling
        new_reservation = await slot_repo.reserve_slot(
            user_id=current_user.id,
            slot_id=reservation.slot_id,
            reservation_date=reservation.reservation_date
        )

        # Log successful reservation for audit trail
        background_tasks.add_task(
            log_activity,
            user_id=current_user.id,
            action="slot_reserved",
            resource_id=new_reservation.id,
            details=f"Slot {reservation.slot_id} reserved"
        )

        return SlotReservationResponse(
            id=new_reservation.id,
            user_id=new_reservation.user_id,
            slot_id=new_reservation.slot_id,
            reserved_at=new_reservation.reserved_at,
            status=new_reservation.status
        )

    except HTTPException as e:
        # Re-raise HTTP exceptions with proper status codes
        logger.warning(f"Slot reservation failed: {e.detail}")
        raise

    except Exception as e:
        # Log unexpected errors but don't expose details to client
        logger.error(f"Unexpected error during slot reservation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your request."
        )
