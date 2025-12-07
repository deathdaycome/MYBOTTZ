"""
Structured logging configuration using structlog
"""

import logging
import sys
from typing import Any
import structlog
from structlog.types import EventDict, WrappedLogger
from pathlib import Path

from app.core.config import settings


# ============================================
# LOG PROCESSORS
# ============================================

def add_app_context(logger: WrappedLogger, method_name: str, event_dict: EventDict) -> EventDict:
    """
    Add application context to log events
    """
    event_dict["app"] = settings.APP_NAME
    event_dict["env"] = settings.ENV
    event_dict["version"] = settings.VERSION
    return event_dict


def add_log_level(logger: WrappedLogger, method_name: str, event_dict: EventDict) -> EventDict:
    """
    Add log level to event dict
    """
    if method_name == "warn":
        method_name = "warning"
    event_dict["level"] = method_name.upper()
    return event_dict


# ============================================
# LOGGING CONFIGURATION
# ============================================

def setup_logging():
    """
    Configure structured logging with structlog
    """
    # Ensure log directory exists
    log_dir = Path(settings.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # Determine log format
    if settings.LOG_FORMAT == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            add_app_context,
            add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            renderer,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )

    # Configure file handler if needed
    if not settings.is_development:
        from logging.handlers import RotatingFileHandler

        file_handler = RotatingFileHandler(
            settings.LOG_FILE,
            maxBytes=settings.LOG_MAX_BYTES,
            backupCount=settings.LOG_BACKUP_COUNT,
        )
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        logging.root.addHandler(file_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)


# ============================================
# LOGGER INSTANCE
# ============================================

# Setup logging on module import
setup_logging()

# Get logger instance
logger: structlog.stdlib.BoundLogger = structlog.get_logger()


# ============================================
# LOGGING UTILITIES
# ============================================

def log_request(method: str, url: str, status_code: int, duration: float, **kwargs):
    """
    Log HTTP request
    """
    logger.info(
        "http_request",
        method=method,
        url=url,
        status_code=status_code,
        duration_ms=round(duration * 1000, 2),
        **kwargs,
    )


def log_database_query(query: str, duration: float, **kwargs):
    """
    Log database query
    """
    logger.debug(
        "database_query",
        query=query[:200],  # Limit query length
        duration_ms=round(duration * 1000, 2),
        **kwargs,
    )


def log_error(error: Exception, context: dict = None, **kwargs):
    """
    Log error with context
    """
    logger.error(
        "error_occurred",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {},
        **kwargs,
        exc_info=True,
    )


def log_audit(action: str, user_id: int = None, entity_type: str = None, entity_id: int = None, changes: dict = None, **kwargs):
    """
    Log audit trail event
    """
    logger.info(
        "audit_event",
        action=action,
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        changes=changes,
        **kwargs,
    )


def log_performance(operation: str, duration: float, **kwargs):
    """
    Log performance metric
    """
    logger.info(
        "performance_metric",
        operation=operation,
        duration_ms=round(duration * 1000, 2),
        **kwargs,
    )


# ============================================
# CORRELATION ID SUPPORT
# ============================================

from contextvars import ContextVar
import uuid

# Correlation ID context variable
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default=None)


def get_correlation_id() -> str:
    """
    Get current correlation ID or generate new one
    """
    cid = correlation_id_var.get()
    if cid is None:
        cid = str(uuid.uuid4())
        correlation_id_var.set(cid)
    return cid


def set_correlation_id(cid: str):
    """
    Set correlation ID for current context
    """
    correlation_id_var.set(cid)
    structlog.contextvars.bind_contextvars(correlation_id=cid)


def clear_correlation_id():
    """
    Clear correlation ID from current context
    """
    correlation_id_var.set(None)
    structlog.contextvars.clear_contextvars()
