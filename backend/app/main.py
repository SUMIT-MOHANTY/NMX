from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, slots, bookings, admin, user
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Passport Appointment Booking API",
    version="1.0.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(slots.router, prefix="/api/slots", tags=["slots"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["bookings"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(user.router, prefix="/api/users", tags=["users"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
