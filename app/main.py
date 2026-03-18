from fastapi import FastAPI, Request, Response
import uvicorn
import logging
from contextlib import asynccontextmanager
import os

# Import the middleware
from app.middleware.rate_limiter import rate_limiter

# Import the routers
from app.routers import auth

# Configure logging
logging_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, logging_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application...")
    yield
    # Shutdown
    logger.info("Shutting down application...")

# Create the FastAPI app
app = FastAPI(
    title="JWT Authentication API",
    description="API for JWT-based authentication",
    version="1.0.0",
    lifespan=lifespan
)

# Add rate limiting middleware
@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    return await rate_limiter.check_rate_limit(request, call_next)

# Add CORS middleware if needed
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Include routers
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "JWT Authentication API is running. Go to /docs for the API documentation."}

# For direct execution
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
