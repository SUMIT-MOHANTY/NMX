from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import auth, slots, bookings, admin
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Passport Appointment Booking System API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
origins = [
    settings.FRONTEND_URL,
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create API router
api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(slots.router, prefix="/slots", tags=["Slots"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])

# Add the API router to the main app
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Welcome to the Passport Appointment Booking System API"}

@app.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "healthy"}
