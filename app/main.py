"""
Enterprise CRM - FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import logger
from app.core.database import engine, check_connection, close_db_connection
from app.core.redis import redis_manager
from app.core.middleware import (
    get_cors_middleware,
    RequestIDMiddleware,
    LoggingMiddleware,
    PrometheusMiddleware,
    ErrorHandlerMiddleware,
    SecurityHeadersMiddleware,
    TimingMiddleware,
    RateLimitMiddleware,
    metrics_endpoint,
    health_check,
    readiness_check,
    liveness_check,
)
from app.core.versioning import APIVersioningMiddleware


# ============================================
# APPLICATION LIFESPAN
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # ==== STARTUP ====
    logger.info(
        "application_startup",
        app_name=settings.APP_NAME,
        version=settings.VERSION,
        environment=settings.ENV,
    )

    # Check database connection
    logger.info("database_connection_check")
    db_ok = await check_connection()
    if not db_ok:
        logger.error("database_connection_failed")
        raise RuntimeError("Database connection failed")
    logger.info("database_connection_ok")

    # Check Redis connection
    logger.info("redis_connection_check")
    redis_ok = await redis_manager.ping()
    if not redis_ok:
        logger.error("redis_connection_failed")
        raise RuntimeError("Redis connection failed")
    logger.info("redis_connection_ok")

    # Initialize metrics
    logger.info("initializing_metrics")
    from app.core.metrics import init_application_info, update_system_metrics

    init_application_info()
    update_system_metrics()
    logger.info("metrics_initialized")

    # Application is ready
    logger.info(
        "application_ready",
        message=f"{settings.APP_NAME} v{settings.VERSION} is ready to serve requests",
    )

    yield

    # ==== SHUTDOWN ====
    logger.info("application_shutdown")

    # Close database connections
    await close_db_connection()
    logger.info("database_connections_closed")

    # Close Redis connections
    await redis_manager.close_all()
    logger.info("redis_connections_closed")

    logger.info("application_shutdown_complete")


# ============================================
# APPLICATION INITIALIZATION
# ============================================

app = FastAPI(
    title=settings.APP_NAME,
    description=f"{settings.APP_NAME} - Enterprise CRM System",
    version=settings.VERSION,
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
    openapi_url=None if not settings.is_development else "/openapi.json",
    lifespan=lifespan,
)


# ============================================
# MIDDLEWARE STACK
# ============================================

# Order matters! Middleware is executed from bottom to top

# 1. CORS (must be first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Response-Time", "Server-Timing"],
)

# 2. Security headers
app.add_middleware(SecurityHeadersMiddleware)

# 3. API Versioning
app.add_middleware(APIVersioningMiddleware)

# 4. Error handler (catch all errors)
app.add_middleware(ErrorHandlerMiddleware)

# 5. Rate limiting
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(
        RateLimitMiddleware,
        max_requests=settings.RATE_LIMIT_PER_MINUTE,
        window=60,  # 1 minute
    )

# 6. Prometheus metrics
app.add_middleware(PrometheusMiddleware)

# 7. Request timing
app.add_middleware(TimingMiddleware)

# 8. Logging
app.add_middleware(LoggingMiddleware)

# 9. Request ID
app.add_middleware(RequestIDMiddleware)


# ============================================
# HEALTH CHECK ENDPOINTS
# ============================================

@app.get("/health", tags=["Health"])
async def health(request: Request):
    """Basic health check"""
    return await health_check(request)


@app.get("/ready", tags=["Health"])
async def ready(request: Request):
    """Readiness check (checks dependencies)"""
    return await readiness_check(request)


@app.get("/live", tags=["Health"])
async def live(request: Request):
    """Liveness check (simple ping)"""
    return await liveness_check(request)


# ============================================
# METRICS ENDPOINT
# ============================================

@app.get("/metrics", tags=["Monitoring"])
async def metrics(request: Request):
    """Prometheus metrics endpoint"""
    return await metrics_endpoint(request)


# ============================================
# API DOCUMENTATION
# ============================================

if settings.is_development:
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        """Custom Swagger UI"""
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title=f"{settings.APP_NAME} - API Docs",
            swagger_favicon_url="/static/favicon.ico" if settings.is_development else None,
        )

    @app.get("/redoc", include_in_schema=False)
    async def custom_redoc_html():
        """Custom ReDoc"""
        return get_redoc_html(
            openapi_url="/openapi.json",
            title=f"{settings.APP_NAME} - API Docs",
            redoc_favicon_url="/static/favicon.ico" if settings.is_development else None,
        )


# ============================================
# API VERSIONING
# ============================================

from fastapi import APIRouter
from app.core.versioning import get_all_versions, get_version_info

# API v1 Router
api_v1_router = APIRouter(prefix="/api/v1", tags=["v1"])

# Import module routers
from app.modules.users import router as users_router, auth_router

# Import logistics module routers (temporarily commented out - empty routers)
# from app.modules.vehicles.router import router as vehicles_router
# from app.modules.drivers.router import router as drivers_router
# from app.modules.routes.router import router as routes_router
# from app.modules.trips.router import router as trips_router
# from app.modules.boxes.router import router as boxes_router
# from app.modules.deliveries.router import router as deliveries_router
# from app.modules.fuel.router import router as fuel_router
# from app.modules.warehouses.router import router as warehouses_router

# Import integration routers (temporarily commented out)
# from app.integrations.wildberries.router import router as wildberries_router

# Import transcription router
from app.api.transcription import router as transcription_router

# Register module routers to API v1
api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(transcription_router)

# Register logistics routers (temporarily commented out)
# api_v1_router.include_router(vehicles_router)
# api_v1_router.include_router(drivers_router)
# api_v1_router.include_router(routes_router)
# api_v1_router.include_router(trips_router)
# api_v1_router.include_router(boxes_router)
# api_v1_router.include_router(deliveries_router)
# api_v1_router.include_router(fuel_router)
# api_v1_router.include_router(warehouses_router)

# Register integration routers (temporarily commented out)
# api_v1_router.include_router(wildberries_router)

# Note: transcription router is mounted separately at /admin/v1 (see line 349)


# ============ Version Info Endpoints ============

@api_v1_router.get("/")
async def api_v1_root():
    """API v1 root endpoint"""
    return {
        "message": "Welcome to API v1",
        "version": "1.0.0",
        "status": "stable",
        "endpoints": {
            "auth": {
                "register": "/api/v1/auth/register",
                "login": "/api/v1/auth/login",
                "refresh": "/api/v1/auth/refresh",
            },
            "users": {
                "me": "/api/v1/users/me",
                "list": "/api/v1/users/",
                "statistics": "/api/v1/users/statistics/overview",
            },
            "logistics": {
                "vehicles": "/api/v1/vehicles",
                "drivers": "/api/v1/drivers",
                "routes": "/api/v1/routes",
                "trips": "/api/v1/trips",
                "boxes": "/api/v1/boxes",
                "deliveries": "/api/v1/deliveries",
                "fuel": "/api/v1/fuel",
                "warehouses": "/api/v1/warehouses",
            },
            "integrations": {
                "wildberries": "/api/v1/wildberries",
            },
            "transcription": {
                "upload_chunk": "/api/v1/transcription/upload-chunk",
                "finalize": "/api/v1/transcription/finalize",
                "upload_video": "/api/v1/transcription/upload-video",
                "status": "/api/v1/transcription/status/{task_id}",
                "download": "/api/v1/transcription/download/{filename}",
                "health": "/api/v1/transcription/health",
            },
            "system": {
                "health": "/health",
                "metrics": "/metrics",
                "docs": "/docs",
                "versions": "/api/versions",
            },
        },
    }


@api_v1_router.get("/version")
async def get_v1_version():
    """Get v1 version information"""
    return get_version_info("v1")


# ============ API Versions Endpoint (Unversioned) ============

@app.get("/api/versions", tags=["API Versioning"])
async def list_api_versions():
    """
    List all available API versions

    Returns information about all API versions including:
    - Version number
    - Status (stable, beta, deprecated)
    - Release date
    - Deprecation and sunset dates (if applicable)
    """
    return get_all_versions()


@app.get("/api/versions/{version}", tags=["API Versioning"])
async def get_api_version_info(version: str):
    """Get detailed information about a specific API version"""
    return get_version_info(version)


# Register API routers
app.include_router(api_v1_router)

logger.info("api_routes_registered", message="Users module routes registered")


# ============================================
# LEGACY ROUTES COMPATIBILITY
# ============================================

# Import legacy admin panel and other routes if needed
try:
    from app.admin.app import admin_router, ui_permissions_router, catch_all_router
    from app.api.miniapp import router as miniapp_router

    # Mount React admin assets BEFORE admin router
    from fastapi.staticfiles import StaticFiles
    app.mount("/admin/assets", StaticFiles(directory="app/admin/static/assets"), name="admin-react-assets")

    # Mount legacy routes (WITHOUT catch-all router)
    app.include_router(admin_router, prefix="/admin", tags=["Admin Panel"])
    if ui_permissions_router is not None:
        app.include_router(ui_permissions_router, prefix="", tags=["Admin Panel"])
    app.include_router(miniapp_router, prefix="/api", tags=["MiniApp"])

    logger.info("legacy_routes_mounted")

except ImportError as e:
    logger.warning("legacy_routes_not_found", error=str(e))
    catch_all_router = None

# Register voice assistant router (WebSocket - MUST be BEFORE catch-all router)
from app.api.voice_assistant import router as voice_assistant_router
app.include_router(voice_assistant_router, tags=["Voice Assistant"])
print("Роутер AI голосового помощника подключен")

# Register voice assistant V2 router (Advanced context management)
from app.api.voice_assistant_v2 import router as voice_assistant_v2_router
app.include_router(voice_assistant_v2_router, tags=["Voice Assistant V2"])
print("Роутер AI голосового помощника V2 (с контекстным менеджером) подключен")

# Register catch-all router LAST to avoid intercepting other routes
if catch_all_router:
    app.include_router(catch_all_router, prefix="/admin", tags=["React Catch-All"])
    logger.info("catch_all_router_mounted", message="Catch-all router registered as last route")


# ============================================
# ROOT ENDPOINT
# ============================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV,
        "status": "operational",
        "api_v1": "/api/v1",
        "docs": "/docs" if settings.is_development else None,
        "health": "/health",
        "metrics": "/metrics",
    }


# ============================================
# CUSTOM OPENAPI
# ============================================

def custom_openapi():
    """Custom OpenAPI schema"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=f"{settings.APP_NAME} API",
        version=settings.VERSION,
        description=f"""
# {settings.APP_NAME} API

Enterprise CRM system with modular architecture.

## Features
- **Authentication**: JWT-based authentication
- **Authorization**: Role-based access control (RBAC)
- **Monitoring**: Prometheus metrics
- **Logging**: Structured JSON logging
- **Rate Limiting**: Redis-based rate limiting
- **Audit Trail**: Complete audit logging

## Environments
- **Development**: Full API documentation and debug info
- **Production**: Optimized for performance and security
        """,
        routes=app.routes,
    )

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# ============================================
# EXCEPTION HANDLERS
# ============================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Not found",
            "path": str(request.url),
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Custom 500 handler"""
    logger.error("internal_server_error", error=str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# ============================================
# STARTUP MESSAGE
# ============================================

if __name__ == "__main__":
    import uvicorn

    logger.info(
        "starting_uvicorn",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.is_development,
    )

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.is_development,
        log_config=None,  # Use our custom logging
    )
