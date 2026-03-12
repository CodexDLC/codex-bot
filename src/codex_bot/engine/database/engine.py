"""
Database engine factory for codex-bot.
Optimized for async bot workflows (SQLite/PostgreSQL).
"""

from typing import Any

from sqlalchemy import Engine, event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool, QueuePool


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
    """
    Setup SQLite for high-performance async workflows.
    Activates WAL mode and foreign keys.

    Checks for both 'sqlite3' (sync) and 'aiosqlite' (async) modules.
    """
    module_name = type(dbapi_connection).__module__
    if module_name.startswith("sqlite3") or module_name.startswith("aiosqlite"):
        cursor = dbapi_connection.cursor()

        # Performance & Consistency Pragmas
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA foreign_keys=ON")

        cursor.close()


def build_engine(url: str, echo: bool = False, **kwargs: Any) -> AsyncEngine:
    """
    Creates a production-ready async SQLAlchemy engine.

    Features:
    - Auto-detection of SQLite vs Postgres settings.
    - Pre-ping to avoid dead connections.
    - Automatic PRAGMA setup for SQLite via event listeners.
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
