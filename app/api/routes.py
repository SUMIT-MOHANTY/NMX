from fastapi import APIRouter
from app.api.endpoints import slots

api_router = APIRouter()
api_router.include_router(slots.router, prefix="/slots", tags=["slots"])
