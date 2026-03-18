from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import auth

app = FastAPI(title="Passport Appointment Booking System")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "Passport Appointment Booking System API"}
