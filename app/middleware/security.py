from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import os
import logging

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        enable_https_redirect=False,
        hsts_max_age=31536000,  # 1 year
        include_subdomains=True
    ):
        super().__init__(app)
        self.enable_https_redirect = enable_https_redirect
        self.hsts_max_age = hsts_max_age
        self.include_subdomains = include_subdomains

    async def dispatch(self, request: Request, call_next):
        # Redirect HTTP to HTTPS in production
        if self.enable_https_redirect and request.url.scheme == "http":
            https_url = str(request.url).replace("http://", "https://", 1)
            return Response(
                status_code=301,
                headers={"Location": https_url}
            )

        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        # Add HSTS header in production
        if self.enable_https_redirect or request.url.scheme == "https":
            hsts_header = f"max-age={self.hsts_max_age}"
            if self.include_subdomains:
                hsts_header += "; includeSubDomains"
            response.headers["Strict-Transport-Security"] = hsts_header

        return response
