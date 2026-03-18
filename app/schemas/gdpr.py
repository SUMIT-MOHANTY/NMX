from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, UUID4

class BookingExport(BaseModel):
    id: UUID4
    slot_id: UUID4
    start_time: datetime
    end_time: datetime
    location: str
    status: str
    created_at: datetime

class UserExportResponse(BaseModel):
    profile: dict
    bookings: List[BookingExport]

class UserDeletionConfirmation(BaseModel):
    message: str
    data_retention_period_days: int = 14
