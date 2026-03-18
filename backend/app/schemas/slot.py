from typing import List, Optional
from pydantic import BaseModel
from datetime import date, time
from uuid import UUID

class SlotBase(BaseModel):
    office_id: UUID
    slot_date: date
    slot_time: time
    capacity: int

class SlotCreate(SlotBase):
    pass

class SlotResponse(SlotBase):
    id: UUID
    taken: int
    available: int

    class Config:
        orm_mode = True

class PaginatedSlotResponse(BaseModel):
    items: List[SlotResponse]
    total: int
    page: int
    size: int
    pages: int
