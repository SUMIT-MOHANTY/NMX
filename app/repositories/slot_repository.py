from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, and_, func
from sqlalchemy.exc import SQLAlchemyError
from app.models.slot import Slot
from app.models.reservation import Reservation
from app.models.user import User
from datetime import datetime
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class SlotRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_available_slot(self, slot_id: int, reservation_date: datetime = None):
        try:
            # Check if the slot exists and is available
            query = select(Slot).where(
                and_(
                    Slot.id == slot_id,
                    Slot.is_active == True
                )
            )

            result = await self.db.execute(query)
            slot = result.scalars().first()

            if not slot:
                raise HTTPException(status_code=404, detail="Slot not found or not available")

            # Check if the slot is already reserved for the given date
            if reservation_date:
                reservation_query = select(Reservation).where(
                    and_(
                        Reservation.slot_id == slot_id,
                        Reservation.reservation_date == reservation_date,
                        Reservation.status == "confirmed"
                    )
                )
                reservation_result = await self.db.execute(reservation_query)
                existing_reservation = reservation_result.scalars().first()

                if existing_reservation:
                    raise HTTPException(status_code=409, detail="Slot already reserved for this date")

            return slot
        except SQLAlchemyError as e:
            logger.error(f"Database error when checking slot availability: {e}")
            raise HTTPException(status_code=500, detail="Database error occurred")

    async def reserve_slot(self, user_id: int, slot_id: int, reservation_date: datetime = None):
        try:
            # Create a new reservation with a database transaction
            new_reservation = Reservation(
                user_id=user_id,
                slot_id=slot_id,
                reserved_at=datetime.utcnow(),
                reservation_date=reservation_date or datetime.utcnow(),
                status="confirmed"
            )

            self.db.add(new_reservation)
            await self.db.flush()  # Ensure we get the ID back but keep in transaction

            # Update slot availability if needed
            await self.db.execute(
                update(Slot)
                .where(Slot.id == slot_id)
                .values(last_reserved=datetime.utcnow())
            )

            # Commit transaction
            await self.db.commit()
            await self.db.refresh(new_reservation)

            return new_reservation
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error when reserving slot: {e}")
            raise HTTPException(status_code=500, detail="Failed to reserve slot")
