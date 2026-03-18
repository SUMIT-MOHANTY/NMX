import time
from typing import Dict, Tuple, Callable
import logging
from fastapi import Request, Response
import os

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        # Store client IP -> (last request timestamp, request count in window)
        self.clients: Dict[str, Tuple[float, int]] = {}
        # Window size in seconds
        try:
            self.window = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
            # Max requests per window
            self.max_requests = int(os.getenv("RATE_LIMIT_MAX", "30"))
        except ValueError:
            logger.warning("Invalid rate limit settings, using defaults")
            self.window = 60
            self.max_requests = 30

    async def check_rate_limit(self, request: Request, call_next: Callable) -> Response:
        """
        FastAPI middleware to implement rate limiting based on client IP
        """
        client_ip = request.client.host if request.client else "unknown"

        # Rate limiting for authentication routes only
        if "/auth/" in request.url.path:
            current_time = time.time()

            # Clear expired entries
            self.clients = {
                ip: (timestamp, count)
                for ip, (timestamp, count) in self.clients.items()
                if current_time - timestamp < self.window
            }

            # Check if client exists and update or create
            if client_ip in self.clients:
                timestamp, count = self.clients[client_ip]

                # If within window and over limit
                if count >= self.max_requests:
                    logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                    headers = {
                        "Retry-After": str(int(timestamp + self.window - current_time)),
                        "X-RateLimit-Limit": str(self.max_requests),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(timestamp + self.window))
                    }
                    return Response(
                        content='{"detail":"Rate limit exceeded"}',
                        status_code=429,
                        headers=headers,
                        media_type="application/json"
                    )

                # Update count
                self.clients[client_ip] = (timestamp, count + 1)
            else:
                # First request in window
                self.clients[client_ip] = (current_time, 1)

        # Process the request if rate limit not exceeded
        return await call_next(request)

rate_limiter = RateLimiter()
