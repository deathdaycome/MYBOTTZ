"""
Alembic environment configuration for async SQLAlchemy
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import your app's base and models
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
# Import Base from separate file to avoid triggering engine creation
from app.core.base import Base

# Import all models here to ensure they're registered with Base.metadata
# Note: importing models is safe - they just define table structures
try:
    from app.core.audit import AuditLog
except ImportError:
    pass  # May not exist yet

# Module models - Import directly without triggering package __init__
try:
    import importlib.util
    import sys
    from pathlib import Path

    # Direct import of models.py to avoid package __init__ execution
    models_path = Path(__file__).parent.parent / "app" / "modules" / "users" / "models.py"
    if models_path.exists():
        spec = importlib.util.spec_from_file_location("users_models", models_path)
        users_models = importlib.util.module_from_spec(spec)
        sys.modules["users_models"] = users_models
        spec.loader.exec_module(users_models)

        # Extract the model classes
        User = users_models.User
        UserSession = users_models.UserSession
        UserActivity = users_models.UserActivity
except Exception as e:
    import warnings
    warnings.warn(f"Could not import user models: {e}")
    pass  # May not exist yet in early setup

# When you create more models, import them here:
# from app.modules.vehicles.models import Vehicle
# from app.modules.drivers.models import Driver

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override sqlalchemy.url with our settings
config.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    Helper function to run migrations with a connection
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations in async mode (online mode)
    """
    # Get async engine configuration from alembic.ini
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = str(settings.DATABASE_URL)

    # Create async engine
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Don't use connection pooling for migrations
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (with async support)."""
    # Check if we're in an async context
    try:
        # Try to get the current event loop
        asyncio.get_running_loop()
        # If we get here, we're already in an async context
        # This shouldn't happen in normal Alembic usage
        raise RuntimeError(
            "run_migrations_online() is called from an async context. "
            "Please use 'asyncio.run(run_async_migrations())' instead."
        )
    except RuntimeError:
        # No event loop running, we can create one
        asyncio.run(run_async_migrations())


# Determine which mode to run
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
