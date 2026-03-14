"""
Async Database Factory — Optimized SQLAlchemy engine orchestration.

Provides a centralized mechanism for creating and configuring asynchronous
SQLAlchemy engines and session factories. Implements backend-specific
optimizations for SQLite (WAL mode, foreign keys) and PostgreSQL (pool
management).
"""

from typing import Any, TypeVar

from sqlalchemy import Engine, event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool, QueuePool

ModelType = TypeVar("ModelType")


def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
    """Configures SQLite connections for high-performance concurrent access.

    This listener activates Write-Ahead Logging (WAL) and enforces foreign key
    constraints, significantly improving reliability and performance in
    asynchronous multi-user bot scenarios.

    Args:
        dbapi_connection: The raw PEP 249 connection object.
        connection_record: The internal SQLAlchemy connection record.
    """
    module_name = type(dbapi_connection).__module__
    if module_name.startswith("sqlite3") or module_name.startswith("aiosqlite"):
        # We use Any because DBAPI cursor can vary between divers
        cursor = dbapi_connection.cursor()

        # Performance & Consistency Pragmas
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA foreign_keys=ON")

        cursor.close()


def build_engine(url: str, echo: bool = False, **kwargs: Any) -> AsyncEngine:
    """Assembles a production-ready asynchronous database engine.

    Automatically detects the target dialect and applies specialized
    configuration:
    - SQLite: Uses `NullPool` to prevent lock contention in async environments.
    - PostgreSQL: Uses `QueuePool` with optimized size and overflow settings.

    Args:
        url: The database connection string (RFC-3986).
        echo: Whether to enable standard out logging for SQL statements.
        **kwargs: Additional engine arguments to pass to `create_async_engine`.

    Returns:
        The configured AsyncEngine instance.
    """
    is_sqlite = url.startswith("sqlite")

    engine_kwargs: dict[str, Any] = {
        "echo": echo,
        "pool_pre_ping": True,
        **kwargs,
    }

    if is_sqlite:
        # SQLite: use NullPool to avoid file locks in async multi-connection scenarios
        engine_kwargs["poolclass"] = NullPool
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        # Postgres: use QueuePool for efficient connection reuse
        engine_kwargs.update(
            {
                "poolclass": QueuePool,
                "pool_size": 10,
                "max_overflow": 20,
            }
        )

    return create_async_engine(url, **engine_kwargs)


def build_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Creates a standardized async session factory."""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


# Register listeners
event.listen(Engine, "connect", set_sqlite_pragma)
