"""
API Versioning System
Provides version negotiation, deprecation warnings, and version management
"""

from typing import Optional, Dict, Any, Callable
from datetime import datetime, date
from fastapi import Request, Response, HTTPException
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import re

from app.core.logging import logger


# ============================================
# VERSION CONFIGURATION
# ============================================

API_VERSIONS = {
    "v1": {
        "version": "1.0.0",
        "status": "stable",
        "released": date(2025, 1, 1),
        "deprecated": None,
        "sunset": None,
        "description": "Current stable API version",
    },
    # Future versions can be added here
    # "v2": {
    #     "version": "2.0.0",
    #     "status": "beta",
    #     "released": date(2025, 6, 1),
    #     "deprecated": None,
    #     "sunset": None,
    #     "description": "Next generation API with improved performance",
    # }
}

DEFAULT_VERSION = "v1"
SUPPORTED_VERSIONS = list(API_VERSIONS.keys())


# ============================================
# VERSION DETECTION
# ============================================

def extract_version_from_path(path: str) -> Optional[str]:
    """
    Extract API version from URL path
    Examples:
        /api/v1/users -> v1
        /api/v2/products -> v2
        /users -> None (no version)
    """
    match = re.match(r"^/api/(v\d+)/", path)
    if match:
        return match.group(1)
    return None


def extract_version_from_header(request: Request) -> Optional[str]:
    """
    Extract API version from Accept header
    Examples:
        Accept: application/vnd.crm.v1+json -> v1
        Accept: application/vnd.crm.v2+json -> v2
    """
    accept_header = request.headers.get("accept", "")
    match = re.search(r"application/vnd\.crm\.(v\d+)\+json", accept_header)
    if match:
        return match.group(1)
    return None


def get_requested_version(request: Request) -> str:
    """
    Determine the API version to use for this request
    Priority:
        1. URL path version (/api/v1/...)
        2. Accept header version (Accept: application/vnd.crm.v1+json)
        3. X-API-Version header
        4. Default version
    """
    # 1. Check URL path
    version = extract_version_from_path(request.url.path)
    if version and version in SUPPORTED_VERSIONS:
        return version

    # 2. Check Accept header
    version = extract_version_from_header(request)
    if version and version in SUPPORTED_VERSIONS:
        return version

    # 3. Check X-API-Version header
    version = request.headers.get("x-api-version")
    if version and version in SUPPORTED_VERSIONS:
        return version

    # 4. Use default
    return DEFAULT_VERSION


# ============================================
# DEPRECATION WARNINGS
# ============================================

class DeprecationWarning:
    """Manages API deprecation warnings"""

    @staticmethod
    def is_deprecated(version: str) -> bool:
        """Check if a version is deprecated"""
        if version not in API_VERSIONS:
            return False
        return API_VERSIONS[version]["deprecated"] is not None

    @staticmethod
    def is_sunset(version: str) -> bool:
        """Check if a version has reached sunset (should be removed)"""
        if version not in API_VERSIONS:
            return False
        sunset_date = API_VERSIONS[version]["sunset"]
        if sunset_date is None:
            return False
        return date.today() >= sunset_date

    @staticmethod
    def get_deprecation_info(version: str) -> Optional[Dict[str, Any]]:
        """Get deprecation information for a version"""
        if not DeprecationWarning.is_deprecated(version):
            return None

        version_info = API_VERSIONS[version]
        return {
            "deprecated": True,
            "deprecated_since": version_info["deprecated"].isoformat() if version_info["deprecated"] else None,
            "sunset_date": version_info["sunset"].isoformat() if version_info["sunset"] else None,
            "message": f"API version {version} is deprecated. Please migrate to {DEFAULT_VERSION}.",
            "documentation": f"/docs/migration/{version}-to-{DEFAULT_VERSION}",
        }

    @staticmethod
    def add_deprecation_headers(response: Response, version: str) -> None:
        """Add deprecation warning headers to response"""
        if not DeprecationWarning.is_deprecated(version):
            return

        version_info = API_VERSIONS[version]

        # Deprecation header (RFC 8594)
        response.headers["Deprecation"] = "true"

        # Sunset header (RFC 8594)
        if version_info["sunset"]:
            response.headers["Sunset"] = version_info["sunset"].isoformat()

        # Link to documentation
        response.headers["Link"] = f'</docs/migration/{version}-to-{DEFAULT_VERSION}>; rel="deprecation"'

        # Warning header
        response.headers["Warning"] = (
            f'299 - "API version {version} is deprecated. '
            f'Please migrate to {DEFAULT_VERSION} before '
            f'{version_info["sunset"].isoformat() if version_info["sunset"] else "sunset date"}."'
        )


# ============================================
# VERSIONING MIDDLEWARE
# ============================================

class APIVersioningMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API version negotiation and deprecation warnings
    """

    async def dispatch(self, request: Request, call_next: Callable):
        # Determine requested version
        version = get_requested_version(request)

        # Check if version is sunset (should no longer be used)
        if DeprecationWarning.is_sunset(version):
            logger.warning(
                "api_version_sunset",
                version=version,
                path=request.url.path,
                client_ip=request.client.host,
            )
            return JSONResponse(
                status_code=410,  # Gone
                content={
                    "error": "API version no longer available",
                    "version": version,
                    "sunset_date": API_VERSIONS[version]["sunset"].isoformat(),
                    "current_version": DEFAULT_VERSION,
                    "message": f"API version {version} is no longer available. Please use {DEFAULT_VERSION}.",
                },
            )

        # Store version in request state for later use
        request.state.api_version = version

        # Log version usage
        logger.debug(
            "api_version_detected",
            version=version,
            path=request.url.path,
        )

        # Process request
        response = await call_next(request)

        # Add version headers to response
        response.headers["X-API-Version"] = version
        response.headers["X-API-Version-Status"] = API_VERSIONS[version]["status"]

        # Add deprecation warnings if needed
        if DeprecationWarning.is_deprecated(version):
            DeprecationWarning.add_deprecation_headers(response, version)
            logger.warning(
                "api_version_deprecated_usage",
                version=version,
                path=request.url.path,
                client_ip=request.client.host,
            )

        return response


# ============================================
# VERSION INFO ENDPOINT DECORATOR
# ============================================

def add_version_info(route_class: APIRoute = APIRoute):
    """
    Decorator to add version information to endpoint metadata
    """
    class VersionedRoute(route_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Add version info to endpoint metadata
            if not hasattr(self, "operation_id"):
                return

            # Version will be detected from path or headers at runtime

    return VersionedRoute


# ============================================
# VERSION UTILITY FUNCTIONS
# ============================================

def get_version_info(version: str) -> Dict[str, Any]:
    """Get detailed information about an API version"""
    if version not in API_VERSIONS:
        raise HTTPException(
            status_code=404,
            detail=f"API version {version} not found"
        )

    info = API_VERSIONS[version].copy()
    info["version_name"] = version

    # Add deprecation info
    deprecation_info = DeprecationWarning.get_deprecation_info(version)
    if deprecation_info:
        info["deprecation"] = deprecation_info

    # Convert dates to ISO format
    if info["released"]:
        info["released"] = info["released"].isoformat()
    if info["deprecated"]:
        info["deprecated"] = info["deprecated"].isoformat()
    if info["sunset"]:
        info["sunset"] = info["sunset"].isoformat()

    return info


def get_all_versions() -> Dict[str, Any]:
    """Get information about all API versions"""
    return {
        "versions": {
            version: get_version_info(version)
            for version in SUPPORTED_VERSIONS
        },
        "default": DEFAULT_VERSION,
        "supported": SUPPORTED_VERSIONS,
    }


# ============================================
# EXPORT
# ============================================

__all__ = [
    "APIVersioningMiddleware",
    "get_requested_version",
    "get_version_info",
    "get_all_versions",
    "DeprecationWarning",
    "add_version_info",
    "API_VERSIONS",
    "DEFAULT_VERSION",
    "SUPPORTED_VERSIONS",
]
