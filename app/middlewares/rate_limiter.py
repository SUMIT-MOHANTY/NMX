from fastapi import Request, HTTPException
import time
from collections import defaultdict
import threading

class RateLimiter:
    def __init__(self, requests_limit: int = 30, window_seconds: int = 60):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
        self.lock = threading.Lock()

    async def __call__(self, request: Request):
        client_ip = request.client.host

        with self.lock:
            current_time = time.time()
            # Remove requests outside the time window
            self.requests[client_ip] = [req_time for req_time in self.requests[client_ip]
                                       if current_time - req_time < self.window_seconds]

            # Check if the request exceeds the rate limit
            if len(self.requests[client_ip]) >= self.requests_limit:
                raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")

            # Add current request timestamp
            self.requests[client_ip].append(current_time)

        return True
