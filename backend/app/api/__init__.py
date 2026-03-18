from fastapi import APIRouter
from .auth import router as auth_router
from .slots import router as slots_router
from .bookings import router as bookings_router
from .admin import router as admin_router
from .user import router as user_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(slots_router, tags=["Slots"])
api_router.include_router(bookings_router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
api_router.include_router(user_router, prefix="/users", tags=["Users"])

__all__ = ["api_router"]
