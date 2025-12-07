"""
Celery application configuration
Background task queue with Redis broker
"""

from celery import Celery
from celery.schedules import crontab
from celery.signals import task_prerun, task_postrun, task_failure
from kombu import Queue, Exchange
import time

from app.core.config import settings
from app.core.logging import logger, set_correlation_id, clear_correlation_id


# ============================================
# CELERY APP INITIALIZATION
# ============================================

celery_app = Celery(
    "crm_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# ============================================
# CELERY CONFIGURATION
# ============================================

celery_app.conf.update(
    # Time zones
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=True,

    # Task settings
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
    task_acks_late=True,
    task_reject_on_worker_lost=True,

    # Result backend settings
    result_expires=settings.CELERY_RESULT_EXPIRES,
    result_backend_transport_options={
        "master_name": "mymaster",
        "visibility_timeout": 3600,
    },

    # Worker settings
    worker_prefetch_multiplier=settings.CELERY_WORKER_PREFETCH_MULTIPLIER,
    worker_max_tasks_per_child=settings.CELERY_WORKER_MAX_TASKS_PER_CHILD,
    worker_disable_rate_limits=False,

    # Queue settings
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",

    # Broker settings
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,

    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)


# ============================================
# QUEUE CONFIGURATION
# ============================================

celery_app.conf.task_queues = (
    Queue("default", Exchange("default"), routing_key="default", priority=5),
    Queue("high_priority", Exchange("high_priority"), routing_key="high_priority", priority=10),
    Queue("low_priority", Exchange("low_priority"), routing_key="low_priority", priority=1),
    Queue("emails", Exchange("emails"), routing_key="emails", priority=3),
    Queue("notifications", Exchange("notifications"), routing_key="notifications", priority=7),
    Queue("reports", Exchange("reports"), routing_key="reports", priority=2),
)

celery_app.conf.task_routes = {
    "app.modules.*.tasks.send_email": {"queue": "emails"},
    "app.modules.*.tasks.send_notification": {"queue": "notifications"},
    "app.modules.*.tasks.generate_report": {"queue": "reports"},
    "app.modules.*.tasks.high_*": {"queue": "high_priority"},
    "app.modules.*.tasks.low_*": {"queue": "low_priority"},
}


# ============================================
# PERIODIC TASKS (BEAT SCHEDULE)
# ============================================

celery_app.conf.beat_schedule = {
    # Cleanup old celery results
    "cleanup-old-results": {
        "task": "app.core.celery_app.cleanup_old_results",
        "schedule": crontab(hour=3, minute=0),  # 3:00 AM daily
    },

    # Check system health
    "health-check": {
        "task": "app.core.celery_app.health_check_task",
        "schedule": 300.0,  # Every 5 minutes
    },

    # Example: Send daily reports
    # "daily-reports": {
    #     "task": "app.modules.analytics.tasks.send_daily_reports",
    #     "schedule": crontab(hour=9, minute=0),  # 9:00 AM daily
    # },

    # Example: Cleanup old data
    # "cleanup-old-data": {
    #     "task": "app.modules.tasks.cleanup_old_data",
    #     "schedule": crontab(hour=2, minute=0, day_of_week=1),  # 2:00 AM every Monday
    # },
}


# ============================================
# TASK AUTO-DISCOVERY
# ============================================

# Auto-discover tasks from all modules
celery_app.autodiscover_tasks(
    [
        "app.modules.users",
        "app.modules.vehicles",
        "app.modules.drivers",
        "app.modules.routes",
        "app.modules.trips",
        "app.modules.fuel",
        "app.modules.boxes",
        "app.modules.deliveries",
        "app.modules.incidents",
        "app.modules.calls",
        "app.modules.analytics",
        "app.modules.wb",
        "app.modules.tasks_new",
    ],
    force=True,
)


# ============================================
# CELERY SIGNALS
# ============================================

@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **extra):
    """
    Called before task execution
    Set up correlation ID for distributed tracing
    """
    set_correlation_id(task_id)
    logger.info(
        "celery_task_started",
        task_id=task_id,
        task_name=task.name,
        args=args,
        kwargs=kwargs,
    )


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **extra):
    """
    Called after task execution
    """
    logger.info(
        "celery_task_completed",
        task_id=task_id,
        task_name=task.name,
        state=state,
        result=str(retval)[:200] if retval else None,
    )
    clear_correlation_id()


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, einfo=None, **extra):
    """
    Called when task fails
    """
    logger.error(
        "celery_task_failed",
        task_id=task_id,
        task_name=sender.name,
        exception=str(exception),
        args=args,
        kwargs=kwargs,
        traceback=str(traceback)[:500] if traceback else None,
        exc_info=True,
    )
    clear_correlation_id()


# ============================================
# BUILT-IN MAINTENANCE TASKS
# ============================================

@celery_app.task(name="app.core.celery_app.cleanup_old_results")
def cleanup_old_results():
    """
    Cleanup old Celery results from Redis
    """
    try:
        from celery.result import AsyncResult

        # This is a placeholder - implement actual cleanup logic
        logger.info("celery_cleanup", message="Cleaning up old results")

        # In production, you might want to:
        # 1. Query old task IDs from result backend
        # 2. Delete results older than X days
        # 3. Log statistics

        return {"status": "success", "cleaned": 0}

    except Exception as e:
        logger.error("celery_cleanup_failed", error=str(e), exc_info=True)
        raise


@celery_app.task(name="app.core.celery_app.health_check_task")
def health_check_task():
    """
    Health check task for monitoring
    """
    try:
        import asyncio
        from app.core.database import check_connection
        from app.core.redis import redis_manager

        # Check database
        db_ok = asyncio.run(check_connection())

        # Check Redis
        redis_ok = asyncio.run(redis_manager.ping())

        status = {
            "celery": "ok",
            "database": "ok" if db_ok else "error",
            "redis": "ok" if redis_ok else "error",
            "timestamp": time.time(),
        }

        logger.info("celery_health_check", **status)
        return status

    except Exception as e:
        logger.error("celery_health_check_failed", error=str(e), exc_info=True)
        return {"celery": "error", "error": str(e)}


# ============================================
# TASK BASE CLASS WITH RETRY LOGIC
# ============================================

class BaseTask(celery_app.Task):
    """
    Base task class with automatic retry logic

    Usage:
        @celery_app.task(base=BaseTask, bind=True, max_retries=3)
        async def my_task(self, arg1, arg2):
            # Task logic here
            pass
    """

    autoretry_for = (Exception,)
    retry_kwargs = {
        "max_retries": 3,
        "countdown": 60,  # Wait 60 seconds before retry
    }
    retry_backoff = True
    retry_backoff_max = 600  # Max 10 minutes
    retry_jitter = True

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried"""
        logger.warning(
            "celery_task_retry",
            task_id=task_id,
            task_name=self.name,
            exception=str(exc),
            retry_count=self.request.retries,
        )

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails after all retries"""
        logger.error(
            "celery_task_failed_final",
            task_id=task_id,
            task_name=self.name,
            exception=str(exc),
            total_retries=self.request.retries,
        )


# ============================================
# UTILITY FUNCTIONS
# ============================================

def get_task_status(task_id: str) -> dict:
    """
    Get status of a Celery task

    Args:
        task_id: Celery task ID

    Returns:
        Dict with task status information
    """
    from celery.result import AsyncResult

    result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "state": result.state,
        "ready": result.ready(),
        "successful": result.successful(),
        "failed": result.failed(),
        "result": result.result if result.ready() else None,
        "traceback": result.traceback,
    }


def revoke_task(task_id: str, terminate: bool = False):
    """
    Revoke/cancel a Celery task

    Args:
        task_id: Celery task ID
        terminate: If True, terminate the task immediately
    """
    celery_app.control.revoke(task_id, terminate=terminate)
    logger.info("celery_task_revoked", task_id=task_id, terminate=terminate)


def inspect_active_tasks() -> dict:
    """
    Get list of active tasks across all workers
    """
    inspect = celery_app.control.inspect()
    return {
        "active": inspect.active(),
        "scheduled": inspect.scheduled(),
        "reserved": inspect.reserved(),
    }


def get_worker_stats() -> dict:
    """
    Get statistics from all workers
    """
    inspect = celery_app.control.inspect()
    return {
        "stats": inspect.stats(),
        "active_queues": inspect.active_queues(),
        "registered": inspect.registered(),
    }


# ============================================
# EXAMPLE TASKS
# ============================================

@celery_app.task(name="app.core.celery_app.example_task", base=BaseTask, bind=True)
def example_task(self, message: str):
    """
    Example task demonstrating best practices
    """
    try:
        logger.info("example_task_started", message=message, task_id=self.request.id)

        # Simulate some work
        time.sleep(2)

        result = {"status": "success", "message": f"Processed: {message}"}
        logger.info("example_task_completed", result=result)

        return result

    except Exception as e:
        logger.error("example_task_failed", error=str(e), exc_info=True)
        # Task will be automatically retried due to BaseTask
        raise


@celery_app.task(name="app.core.celery_app.example_async_task")
async def example_async_task(user_id: int):
    """
    Example async task with database access
    """
    try:
        from app.core.database import get_db_context

        async with get_db_context() as db:
            # Do database operations here
            logger.info("example_async_task", user_id=user_id)

            return {"status": "success", "user_id": user_id}

    except Exception as e:
        logger.error("example_async_task_failed", error=str(e), exc_info=True)
        raise


@celery_app.task(name="app.core.celery_app.example_chain_task")
def example_chain_task(data: dict):
    """
    Example task that can be chained with other tasks

    Usage:
        from celery import chain
        result = chain(
            example_chain_task.s({"step": 1}),
            example_chain_task.s({"step": 2}),
            example_chain_task.s({"step": 3}),
        )()
    """
    logger.info("example_chain_task", data=data)
    data["processed"] = True
    return data
