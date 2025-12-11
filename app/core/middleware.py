"""
FastAPI middleware for monitoring, logging, and request handling
"""

import time
from typing import Callable
from datetime import datetime

from fastapi import Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

from app.core.logging import (
    logger,
    set_correlation_id,
    clear_correlation_id,
    get_correlation_id,
)
from app.core.config import settings


# ============================================
# PROMETHEUS METRICS
# ============================================

# HTTP request metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0),
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests in progress",
    ["method", "endpoint"],
)

http_request_size_bytes = Histogram(
    "http_request_size_bytes",
    "HTTP request size in bytes",
    ["method", "endpoint"],
)

http_response_size_bytes = Histogram(
    "http_response_size_bytes",
    "HTTP response size in bytes",
    ["method", "endpoint"],
)

# Application metrics
active_users_gauge = Gauge(
    "active_users",
    "Number of active users",
)

database_connections_gauge = Gauge(
    "database_connections",
    "Number of active database connections",
)

cache_hits_total = Counter(
    "cache_hits_total",
    "Total cache hits",
)

cache_misses_total = Counter(
    "cache_misses_total",
    "Total cache misses",
)

# Custom business metrics
tasks_created_total = Counter(
    "tasks_created_total",
    "Total tasks created",
    ["project_id"],
)

tasks_completed_total = Counter(
    "tasks_completed_total",
    "Total tasks completed",
    ["project_id"],
)


# ============================================
# REQUEST ID MIDDLEWARE
# ============================================

class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add request ID to all requests for distributed tracing
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get or generate request ID
        request_id = request.headers.get("X-Request-ID", get_correlation_id())

        # Set correlation ID for logging
        set_correlation_id(request_id)

        # Store in request state
        request.state.request_id = request_id

        try:
            # Process request
            response = await call_next(request)

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        finally:
            # Clean up correlation ID
            clear_correlation_id()


# ============================================
# LOGGING MIDDLEWARE
# ============================================

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests and responses
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Get request info
        method = request.method
        url = str(request.url)
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Log request
        logger.info(
            "http_request_received",
            method=method,
            url=url,
            client_ip=client_host,
            user_agent=user_agent,
        )

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response
            logger.info(
                "http_request_completed",
                method=method,
                url=url,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
            )

            return response

        except Exception as e:
            # Log error
            duration = time.time() - start_time

            logger.error(
                "http_request_failed",
                method=method,
                url=url,
                error=str(e),
                duration_ms=round(duration * 1000, 2),
                exc_info=True,
            )

            # Return error response
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"},
            )


# ============================================
# PROMETHEUS METRICS MIDDLEWARE
# ============================================

class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware to collect Prometheus metrics for all requests
    """

    def _get_endpoint_path(self, request: Request) -> str:
        """Get normalized endpoint path for metrics"""
        # Get path from route if available
        if hasattr(request, "scope") and "route" in request.scope:
            route = request.scope["route"]
            if hasattr(route, "path"):
                return route.path

        # Otherwise use raw path (less ideal as it includes IDs)
        return request.url.path

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        method = request.method
        endpoint = self._get_endpoint_path(request)

        # Skip metrics endpoint to avoid recursion
        if endpoint == "/metrics":
            return await call_next(request)

        # Increment in-progress requests
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()

        # Record request size
        request_size = int(request.headers.get("content-length", 0))
        http_request_size_bytes.labels(method=method, endpoint=endpoint).observe(request_size)

        # Start timer
        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Record metrics
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=response.status_code,
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint,
            ).observe(duration)

            # Record response size if available
            if "content-length" in response.headers:
                response_size = int(response.headers["content-length"])
                http_response_size_bytes.labels(
                    method=method,
                    endpoint=endpoint,
                ).observe(response_size)

            return response

        except Exception as e:
            # Record error metric
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=500,
            ).inc()

            raise

        finally:
            # Decrement in-progress requests
            http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()


# ============================================
# ERROR HANDLING MIDDLEWARE
# ============================================

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Global error handler middleware
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)

        except Exception as e:
            logger.error(
                "unhandled_exception",
                error=str(e),
                error_type=type(e).__name__,
                url=str(request.url),
                method=request.method,
                exc_info=True,
            )

            # Return generic error response
            if settings.is_development:
                # In development, show detailed error
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "detail": "Internal server error",
                        "error": str(e),
                        "type": type(e).__name__,
                    },
                )
            else:
                # In production, hide details
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"detail": "Internal server error"},
                )


# ============================================
# SECURITY HEADERS MIDDLEWARE
# ============================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Content Security Policy
        if not settings.is_development:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:;"
            )

        return response


# ============================================
# REQUEST TIMING MIDDLEWARE
# ============================================

class TimingMiddleware(BaseHTTPMiddleware):
    """
    Add Server-Timing header for performance analysis
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Add timing header
        response.headers["Server-Timing"] = f"total;dur={duration * 1000:.2f}"

        # Add custom timing header
        response.headers["X-Response-Time"] = f"{duration * 1000:.2f}ms"

        return response


# ============================================
# CORS CONFIGURATION
# ============================================

def get_cors_middleware():
    """
    Get configured CORS middleware
    """
    return CORSMiddleware(
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Response-Time", "Server-Timing"],
    )


# ============================================
# METRICS ENDPOINT
# ============================================

async def metrics_endpoint(request: Request):
    """
    Prometheus metrics endpoint

    Returns:
        Prometheus metrics in text format
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


# ============================================
# HEALTH CHECK ENDPOINTS
# ============================================

async def health_check(request: Request):
    """
    Basic health check endpoint

    Returns:
        200 OK if application is running
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.VERSION,
        }
    )


async def readiness_check(request: Request):
    """
    Readiness check endpoint (checks dependencies)

    Returns:
        200 OK if application is ready to serve requests
    """
    # Check database
    from app.core.database import check_connection
    db_ok = await check_connection()

    # Check Redis
    from app.core.redis import redis_manager
    redis_ok = await redis_manager.ping()

    # Overall status
    is_ready = db_ok and redis_ok
    status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if is_ready else "not ready",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "database": "ok" if db_ok else "error",
                "redis": "ok" if redis_ok else "error",
            },
        }
    )


async def liveness_check(request: Request):
    """
    Liveness check endpoint (simple ping)

    Returns:
        200 OK if application is alive
    """
    return JSONResponse(
        content={
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


# ============================================
# RATE LIMITING MIDDLEWARE
# ============================================

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Global rate limiting middleware using Redis
    """

    def __init__(self, app, max_requests: int = 100, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks and metrics
        if request.url.path in ["/health", "/ready", "/live", "/metrics"]:
            return await call_next(request)

        # Get client identifier
        client_ip = request.client.host if request.client else "unknown"

        # Try to get user ID from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)

        # Generate rate limit key
        if user_id:
            rate_limit_key = f"rate_limit:user:{user_id}"
        else:
            rate_limit_key = f"rate_limit:ip:{client_ip}"

        # Check rate limit
        from app.core.redis import rate_limiter

        allowed, remaining = await rate_limiter.is_allowed(
            key=rate_limit_key,
            max_requests=self.max_requests,
            window=self.window,
        )

        # Add rate limit headers to response
        async def add_rate_limit_headers(response: Response) -> Response:
            response.headers["X-RateLimit-Limit"] = str(self.max_requests)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.window)
            return response

        if not allowed:
            logger.warning(
                "rate_limit_exceeded",
                client_ip=client_ip,
                user_id=user_id,
                max_requests=self.max_requests,
                window=self.window,
            )

            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Rate limit exceeded. Max {self.max_requests} requests per {self.window} seconds."
                },
            )
            return await add_rate_limit_headers(response)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        return await add_rate_limit_headers(response)
