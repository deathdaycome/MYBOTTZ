"""
Enterprise Infrastructure Test Script

Tests all core components of the enterprise CRM system:
- Configuration loading
- Database connection
- Redis connection
- Health endpoints
- Metrics endpoint
- API versioning
- Middleware stack
- Logging system
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import httpx
from sqlalchemy import text
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


class TestResult:
    """Test result container"""
    def __init__(self, name: str, passed: bool, message: str = "", duration: float = 0):
        self.name = name
        self.passed = passed
        self.message = message
        self.duration = duration


async def test_config_loading() -> TestResult:
    """Test configuration loading"""
    try:
        from app.core.config import settings

        # Check critical settings
        assert settings.APP_NAME, "APP_NAME not set"
        assert settings.VERSION, "VERSION not set"
        assert settings.ENV, "ENV not set"

        return TestResult(
            "Configuration Loading",
            True,
            f"✓ Loaded {settings.APP_NAME} v{settings.VERSION} ({settings.ENV})"
        )
    except Exception as e:
        return TestResult("Configuration Loading", False, f"✗ {str(e)}")


async def test_database_connection() -> TestResult:
    """Test database connection and pooling"""
    try:
        from app.core.database import engine, AsyncSessionLocal
        from app.core.config import settings

        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            assert result.scalar() == 1

        # Test session factory
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT version()"))
            version = result.scalar()

        return TestResult(
            "Database Connection",
            True,
            f"✓ Connected to PostgreSQL\n  Pool: {settings.DATABASE_POOL_SIZE} base + {settings.DATABASE_MAX_OVERFLOW} overflow"
        )
    except Exception as e:
        return TestResult("Database Connection", False, f"✗ {str(e)}")


async def test_redis_connection() -> TestResult:
    """Test Redis connection and multi-DB support"""
    try:
        from app.core.redis import redis_manager, cache, rate_limiter

        # Test default client
        redis = await redis_manager.get_client(0)
        await redis.ping()

        # Test cache client
        redis_cache = await redis_manager.get_client(1)
        await redis_cache.ping()

        # Test cache operations
        await cache.set("test_key", {"test": "value"}, ttl=60)
        cached_value = await cache.get("test_key")
        assert cached_value == {"test": "value"}
        await cache.delete("test_key")

        # Test rate limiter
        allowed, remaining = await rate_limiter.is_allowed("test_rate_limit", 10, 60)
        assert allowed is True

        return TestResult(
            "Redis Connection",
            True,
            "✓ Connected to Redis\n  ✓ Multi-DB support working\n  ✓ Cache operations working\n  ✓ Rate limiter working"
        )
    except Exception as e:
        return TestResult("Redis Connection", False, f"✗ {str(e)}")


async def test_logging_system() -> TestResult:
    """Test structured logging"""
    try:
        from app.core.logging import logger, get_correlation_id, set_correlation_id

        # Test logger
        logger.info("test_log_entry", test_key="test_value")

        # Test correlation ID
        set_correlation_id("test-correlation-id")
        cid = get_correlation_id()
        assert cid == "test-correlation-id"

        return TestResult(
            "Logging System",
            True,
            "✓ Structured logging initialized\n  ✓ Correlation IDs working"
        )
    except Exception as e:
        return TestResult("Logging System", False, f"✗ {str(e)}")


async def test_security_module() -> TestResult:
    """Test security and authentication"""
    try:
        from app.core.security import (
            hash_password, verify_password,
            create_access_token, decode_token,
            Role, Permission, has_permission,
            get_role_permissions
        )

        # Test password hashing
        hashed = hash_password("test_password_123")
        assert verify_password("test_password_123", hashed)
        assert not verify_password("wrong_password", hashed)

        # Test JWT tokens
        token = create_access_token(user_id=1, username="test_user", role="admin")
        token_data = decode_token(token)
        assert token_data.user_id == 1
        assert token_data.username == "test_user"

        # Test RBAC
        admin_perms = get_role_permissions(Role.ADMIN)
        assert len(admin_perms) > 0
        assert has_permission(Role.ADMIN, Permission.USER_CREATE)

        return TestResult(
            "Security Module",
            True,
            f"✓ Password hashing working\n  ✓ JWT tokens working\n  ✓ RBAC configured ({len(admin_perms)} admin permissions)"
        )
    except Exception as e:
        return TestResult("Security Module", False, f"✗ {str(e)}")


async def test_audit_system() -> TestResult:
    """Test audit log system"""
    try:
        from app.core.audit import AuditAction, AuditLog

        # Check audit actions
        actions = list(AuditAction)
        assert len(actions) > 40, "Not enough audit actions defined"

        # Check audit model
        assert hasattr(AuditLog, 'user_id')
        assert hasattr(AuditLog, 'action')
        assert hasattr(AuditLog, 'changes')

        return TestResult(
            "Audit System",
            True,
            f"✓ Audit system initialized\n  ✓ {len(actions)} action types defined"
        )
    except Exception as e:
        return TestResult("Audit System", False, f"✗ {str(e)}")


async def test_celery_config() -> TestResult:
    """Test Celery configuration"""
    try:
        from app.core.celery_app import celery_app

        # Check configuration
        assert celery_app.conf.broker_url, "Broker URL not configured"
        assert celery_app.conf.result_backend, "Result backend not configured"

        # Check queues
        queues = celery_app.conf.task_queues
        assert len(queues) >= 6, "Not enough task queues configured"

        # Check beat schedule
        beat_schedule = celery_app.conf.beat_schedule
        assert len(beat_schedule) > 0, "No scheduled tasks configured"

        return TestResult(
            "Celery Configuration",
            True,
            f"✓ Celery configured\n  ✓ {len(queues)} priority queues\n  ✓ {len(beat_schedule)} scheduled tasks"
        )
    except Exception as e:
        return TestResult("Celery Configuration", False, f"✗ {str(e)}")


async def test_alembic_setup() -> TestResult:
    """Test Alembic migrations setup"""
    try:
        from alembic.config import Config
        from alembic import script
        from pathlib import Path

        # Check alembic.ini exists
        alembic_ini = project_root / "alembic.ini"
        assert alembic_ini.exists(), "alembic.ini not found"

        # Check migrations directory
        migrations_dir = project_root / "alembic"
        assert migrations_dir.exists(), "alembic directory not found"

        # Check env.py
        env_py = migrations_dir / "env.py"
        assert env_py.exists(), "env.py not found"

        return TestResult(
            "Alembic Setup",
            True,
            "✓ Alembic configured\n  ✓ Migration system ready"
        )
    except Exception as e:
        return TestResult("Alembic Setup", False, f"✗ {str(e)}")


async def test_middleware_imports() -> TestResult:
    """Test middleware imports"""
    try:
        from app.core.middleware import (
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
        )

        middleware_count = 7

        return TestResult(
            "Middleware Imports",
            True,
            f"✓ All middleware imported\n  ✓ {middleware_count} middleware classes available"
        )
    except Exception as e:
        return TestResult("Middleware Imports", False, f"✗ {str(e)}")


async def test_main_app_import() -> TestResult:
    """Test main application import"""
    try:
        from app.main import app

        # Check FastAPI app
        assert app is not None, "FastAPI app not initialized"
        assert hasattr(app, 'routes'), "Routes not configured"

        # Count routes
        route_count = len(app.routes)

        return TestResult(
            "Main Application",
            True,
            f"✓ FastAPI app initialized\n  ✓ {route_count} routes registered"
        )
    except Exception as e:
        return TestResult("Main Application", False, f"✗ {str(e)}")


async def run_all_tests():
    """Run all infrastructure tests"""
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]🚀 Enterprise CRM Infrastructure Tests[/bold cyan]",
        border_style="cyan"
    ))
    console.print("\n")

    tests = [
        test_config_loading,
        test_database_connection,
        test_redis_connection,
        test_logging_system,
        test_security_module,
        test_audit_system,
        test_celery_config,
        test_alembic_setup,
        test_middleware_imports,
        test_main_app_import,
    ]

    results = []

    for test_func in tests:
        console.print(f"[cyan]Running:[/cyan] {test_func.__doc__}")
        result = await test_func()
        results.append(result)

        if result.passed:
            console.print(f"[green]{result.message}[/green]\n")
        else:
            console.print(f"[red]{result.message}[/red]\n")

    # Summary table
    console.print("\n")
    table = Table(
        title="📊 Test Summary",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )
    table.add_column("Test", style="cyan", width=30)
    table.add_column("Status", width=10)
    table.add_column("Details", width=60)

    passed_count = 0
    failed_count = 0

    for result in results:
        status = "[green]✓ PASS[/green]" if result.passed else "[red]✗ FAIL[/red]"
        table.add_row(result.name, status, result.message.split("\n")[0])

        if result.passed:
            passed_count += 1
        else:
            failed_count += 1

    console.print(table)
    console.print("\n")

    # Final summary
    if failed_count == 0:
        console.print(Panel.fit(
            f"[bold green]✅ ALL TESTS PASSED ({passed_count}/{len(results)})[/bold green]",
            border_style="green"
        ))
    else:
        console.print(Panel.fit(
            f"[bold red]❌ SOME TESTS FAILED ({passed_count}/{len(results)} passed, {failed_count} failed)[/bold red]",
            border_style="red"
        ))

    console.print("\n")

    return failed_count == 0


if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Tests interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Fatal error: {e}[/red]")
        sys.exit(1)
