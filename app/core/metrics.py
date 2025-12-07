"""
Custom Prometheus Metrics for Enterprise CRM
Provides business-level and application-level metrics
"""

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary,
    Info,
    Enum,
)
from typing import Optional
import psutil
import os


# ============================================
# BUSINESS METRICS
# ============================================

# Projects
projects_total = Gauge(
    "crm_projects_total",
    "Total number of projects",
    ["status"],
)

projects_created_total = Counter(
    "crm_projects_created_total",
    "Total projects created",
    ["project_type"],
)

projects_completed_total = Counter(
    "crm_projects_completed_total",
    "Total projects completed",
    ["project_type"],
)

project_duration_seconds = Histogram(
    "crm_project_duration_seconds",
    "Project completion time in seconds",
    ["project_type"],
    buckets=(
        3600,  # 1 hour
        86400,  # 1 day
        259200,  # 3 days
        604800,  # 1 week
        1209600,  # 2 weeks
        2592000,  # 30 days
        7776000,  # 90 days
    ),
)

# Tasks
tasks_total = Gauge(
    "crm_tasks_total",
    "Total number of tasks",
    ["status", "priority"],
)

tasks_created_total = Counter(
    "crm_tasks_created_total",
    "Total tasks created",
    ["project_id", "priority"],
)

tasks_completed_total = Counter(
    "crm_tasks_completed_total",
    "Total tasks completed",
    ["project_id", "priority"],
)

tasks_overdue_total = Gauge(
    "crm_tasks_overdue_total",
    "Number of overdue tasks",
    ["project_id"],
)

task_completion_time_seconds = Histogram(
    "crm_task_completion_time_seconds",
    "Task completion time in seconds",
    ["priority"],
    buckets=(300, 900, 1800, 3600, 7200, 14400, 28800, 86400),
)

# Users & Authentication
users_total = Gauge(
    "crm_users_total",
    "Total number of users",
    ["role"],
)

users_active_total = Gauge(
    "crm_users_active_total",
    "Number of active users",
    ["role"],
)

login_attempts_total = Counter(
    "crm_login_attempts_total",
    "Total login attempts",
    ["status"],  # success, failed
)

login_duration_seconds = Histogram(
    "crm_login_duration_seconds",
    "Login duration in seconds",
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

user_sessions_active = Gauge(
    "crm_user_sessions_active",
    "Number of active user sessions",
)

# API Tokens
api_tokens_issued_total = Counter(
    "crm_api_tokens_issued_total",
    "Total API tokens issued",
    ["token_type"],  # access, refresh
)

api_tokens_revoked_total = Counter(
    "crm_api_tokens_revoked_total",
    "Total API tokens revoked",
)

# ============================================
# LOGISTICS METRICS
# ============================================

# Vehicles
vehicles_total = Gauge(
    "crm_vehicles_total",
    "Total number of vehicles",
    ["status"],
)

vehicles_active_total = Gauge(
    "crm_vehicles_active_total",
    "Number of active vehicles",
)

vehicle_utilization_ratio = Gauge(
    "crm_vehicle_utilization_ratio",
    "Vehicle utilization ratio (0-1)",
    ["vehicle_id"],
)

# Deliveries
deliveries_total = Gauge(
    "crm_deliveries_total",
    "Total number of deliveries",
    ["status"],
)

deliveries_completed_total = Counter(
    "crm_deliveries_completed_total",
    "Total deliveries completed",
)

delivery_duration_seconds = Histogram(
    "crm_delivery_duration_seconds",
    "Delivery duration in seconds",
    buckets=(1800, 3600, 7200, 14400, 28800, 86400),
)

# Routes
routes_total = Gauge(
    "crm_routes_total",
    "Total number of routes",
    ["status"],
)

route_distance_km = Histogram(
    "crm_route_distance_km",
    "Route distance in kilometers",
    buckets=(10, 25, 50, 100, 250, 500, 1000),
)

# Fuel
fuel_consumption_liters = Counter(
    "crm_fuel_consumption_liters_total",
    "Total fuel consumed in liters",
    ["vehicle_id"],
)

fuel_cost_total = Counter(
    "crm_fuel_cost_total",
    "Total fuel cost",
    ["vehicle_id"],
)

# ============================================
# WILDBERRIES INTEGRATION METRICS
# ============================================

wb_products_synced_total = Counter(
    "crm_wb_products_synced_total",
    "Total WildBerries products synced",
    ["sync_status"],  # success, failed
)

wb_orders_synced_total = Counter(
    "crm_wb_orders_synced_total",
    "Total WildBerries orders synced",
    ["sync_status"],
)

wb_webhooks_received_total = Counter(
    "crm_wb_webhooks_received_total",
    "Total WildBerries webhooks received",
    ["event_type"],
)

wb_api_requests_total = Counter(
    "crm_wb_api_requests_total",
    "Total WildBerries API requests",
    ["endpoint", "status"],
)

wb_api_latency_seconds = Histogram(
    "crm_wb_api_latency_seconds",
    "WildBerries API latency in seconds",
    ["endpoint"],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0),
)

wb_rate_limit_remaining = Gauge(
    "crm_wb_rate_limit_remaining",
    "WildBerries API rate limit remaining",
)

# ============================================
# DATABASE METRICS
# ============================================

db_queries_total = Counter(
    "crm_db_queries_total",
    "Total database queries",
    ["operation"],  # select, insert, update, delete
)

db_query_duration_seconds = Histogram(
    "crm_db_query_duration_seconds",
    "Database query duration in seconds",
    ["operation", "table"],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0),
)

db_connections_total = Gauge(
    "crm_db_connections_total",
    "Total database connections",
    ["state"],  # active, idle
)

db_transactions_total = Counter(
    "crm_db_transactions_total",
    "Total database transactions",
    ["status"],  # committed, rolled_back
)

db_deadlocks_total = Counter(
    "crm_db_deadlocks_total",
    "Total database deadlocks",
)

# ============================================
# REDIS/CACHE METRICS
# ============================================

cache_operations_total = Counter(
    "crm_cache_operations_total",
    "Total cache operations",
    ["operation", "status"],  # get/set/delete, hit/miss
)

cache_hit_ratio = Gauge(
    "crm_cache_hit_ratio",
    "Cache hit ratio (0-1)",
)

cache_size_bytes = Gauge(
    "crm_cache_size_bytes",
    "Cache size in bytes",
)

cache_keys_total = Gauge(
    "crm_cache_keys_total",
    "Total number of cache keys",
)

cache_evictions_total = Counter(
    "crm_cache_evictions_total",
    "Total cache evictions",
)

# ============================================
# CELERY METRICS
# ============================================

celery_tasks_total = Counter(
    "crm_celery_tasks_total",
    "Total Celery tasks",
    ["task_name", "status"],  # success, failure, retry
)

celery_task_duration_seconds = Histogram(
    "crm_celery_task_duration_seconds",
    "Celery task duration in seconds",
    ["task_name"],
    buckets=(0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 300.0),
)

celery_queue_length = Gauge(
    "crm_celery_queue_length",
    "Celery queue length",
    ["queue"],
)

celery_workers_active = Gauge(
    "crm_celery_workers_active",
    "Number of active Celery workers",
)

# ============================================
# SYSTEM METRICS
# ============================================

system_cpu_usage_percent = Gauge(
    "crm_system_cpu_usage_percent",
    "System CPU usage percentage",
)

system_memory_usage_bytes = Gauge(
    "crm_system_memory_usage_bytes",
    "System memory usage in bytes",
    ["type"],  # used, available
)

system_disk_usage_bytes = Gauge(
    "crm_system_disk_usage_bytes",
    "System disk usage in bytes",
    ["type"],  # used, free
)

system_open_file_descriptors = Gauge(
    "crm_system_open_file_descriptors",
    "Number of open file descriptors",
)

# ============================================
# APPLICATION INFO
# ============================================

application_info = Info(
    "crm_application",
    "Application information",
)

application_version = Info(
    "crm_application_version",
    "Application version information",
)

# ============================================
# HELPER FUNCTIONS
# ============================================


def update_system_metrics():
    """Update system-level metrics"""
    try:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        system_cpu_usage_percent.set(cpu_percent)

        # Memory
        memory = psutil.virtual_memory()
        system_memory_usage_bytes.labels(type="used").set(memory.used)
        system_memory_usage_bytes.labels(type="available").set(memory.available)

        # Disk
        disk = psutil.disk_usage("/")
        system_disk_usage_bytes.labels(type="used").set(disk.used)
        system_disk_usage_bytes.labels(type="free").set(disk.free)

        # File descriptors (Unix only)
        try:
            process = psutil.Process(os.getpid())
            num_fds = process.num_fds()
            system_open_file_descriptors.set(num_fds)
        except (AttributeError, NotImplementedError):
            # Not available on Windows
            pass

    except Exception as e:
        # Log but don't crash
        from app.core.logging import logger
        logger.error("metrics_update_failed", error=str(e))


def init_application_info():
    """Initialize application info metrics"""
    from app.core.config import settings

    application_info.info(
        {
            "app_name": settings.APP_NAME,
            "environment": settings.ENV,
            "python_version": os.sys.version,
        }
    )

    application_version.info(
        {
            "version": settings.VERSION,
            "api_version": "v1",
        }
    )


# ============================================
# METRIC COLLECTORS
# ============================================


class MetricsCollector:
    """Helper class for collecting metrics"""

    @staticmethod
    def track_task_created(project_id: Optional[str] = None, priority: str = "medium"):
        """Track task creation"""
        labels = {"project_id": project_id or "unknown", "priority": priority}
        tasks_created_total.labels(**labels).inc()

    @staticmethod
    def track_task_completed(
        project_id: Optional[str] = None,
        priority: str = "medium",
        duration_seconds: float = 0,
    ):
        """Track task completion"""
        labels = {"project_id": project_id or "unknown", "priority": priority}
        tasks_completed_total.labels(**labels).inc()
        if duration_seconds > 0:
            task_completion_time_seconds.labels(priority=priority).observe(
                duration_seconds
            )

    @staticmethod
    def track_login_attempt(success: bool, duration_seconds: float = 0):
        """Track login attempt"""
        status = "success" if success else "failed"
        login_attempts_total.labels(status=status).inc()
        if duration_seconds > 0:
            login_duration_seconds.observe(duration_seconds)

    @staticmethod
    def track_wb_api_request(endpoint: str, status: str, latency_seconds: float = 0):
        """Track WildBerries API request"""
        wb_api_requests_total.labels(endpoint=endpoint, status=status).inc()
        if latency_seconds > 0:
            wb_api_latency_seconds.labels(endpoint=endpoint).observe(latency_seconds)

    @staticmethod
    def track_db_query(operation: str, table: str, duration_seconds: float):
        """Track database query"""
        db_queries_total.labels(operation=operation).inc()
        db_query_duration_seconds.labels(operation=operation, table=table).observe(
            duration_seconds
        )

    @staticmethod
    def track_cache_operation(operation: str, hit: bool):
        """Track cache operation"""
        status = "hit" if hit else "miss"
        cache_operations_total.labels(operation=operation, status=status).inc()


# ============================================
# EXPORT
# ============================================

__all__ = [
    # Collectors
    "MetricsCollector",
    # Functions
    "update_system_metrics",
    "init_application_info",
    # Business metrics
    "projects_total",
    "tasks_total",
    "users_total",
    # Integration metrics
    "wb_api_requests_total",
    "wb_webhooks_received_total",
    # System metrics
    "system_cpu_usage_percent",
    "system_memory_usage_bytes",
]
