"""Security middleware and utilities."""
import os
import time
from typing import Optional, List
from collections import defaultdict
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from optifire.core.logger import logger


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)

    def is_allowed(self, client_ip: str) -> bool:
        """Check if request is allowed based on rate limit."""
        now = time.time()
        minute_ago = now - 60

        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > minute_ago
        ]

        # Check if limit exceeded
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return False

        # Add current request
        self.requests[client_ip].append(now)
        return True


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce IP whitelist."""

    def __init__(self, app, whitelist: Optional[List[str]] = None):
        super().__init__(app)
        self.whitelist = whitelist or []

        # Add whitelist from environment
        env_whitelist = os.getenv("IP_WHITELIST", "")
        if env_whitelist:
            self.whitelist.extend([ip.strip() for ip in env_whitelist.split(",")])

        # Always allow localhost
        if not self.whitelist or "127.0.0.1" not in self.whitelist:
            self.whitelist.extend(["127.0.0.1", "::1", "localhost"])

        logger.info(f"IP Whitelist enabled: {len(self.whitelist)} IPs allowed")

    async def dispatch(self, request: Request, call_next):
        """Check IP whitelist before processing request."""
        client_ip = request.client.host if request.client else "unknown"

        # Skip whitelist check for health endpoint
        if request.url.path == "/health":
            return await call_next(request)

        # Check if IP is whitelisted
        if self.whitelist and client_ip not in self.whitelist:
            logger.warning(f"Blocked request from non-whitelisted IP: {client_ip}")
            return JSONResponse(
                status_code=403,
                content={"detail": "Access denied: IP not whitelisted"}
            )

        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce rate limiting."""

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.rate_limiter = RateLimiter(requests_per_minute)
        logger.info(f"Rate limiting enabled: {requests_per_minute} requests/minute")

    async def dispatch(self, request: Request, call_next):
        """Check rate limit before processing request."""
        client_ip = request.client.host if request.client else "unknown"

        # Skip rate limit for health endpoint
        if request.url.path == "/health":
            return await call_next(request)

        # Check rate limit
        if not self.rate_limiter.is_allowed(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."}
            )

        return await call_next(request)


def get_client_ip(request: Request) -> str:
    """
    Get client IP from request, checking X-Forwarded-For header first.
    Useful when behind a reverse proxy.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For can contain multiple IPs, take the first one
        return forwarded.split(",")[0].strip()

    if request.client:
        return request.client.host

    return "unknown"
