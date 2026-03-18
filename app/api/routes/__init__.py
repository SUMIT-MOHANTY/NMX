from fastapi import APIRouter

# Import all routers
from app.api.routes.gdpr import router as gdpr_router
# Import other routers as well (auth_router, booking_router, etc.)

# Create the main API router
api_router = APIRouter()

# Include all routers
api_router.include_router(gdpr_router, prefix="/api", tags=["gdpr"])
# Include other routers as well
