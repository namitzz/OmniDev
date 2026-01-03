"""
OmniDev Database Connection and Session Management

Provides async database connection and session management.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from .config import settings
from .models import Base
from .logging import get_logger

logger = get_logger(__name__)

# Create async engine
# SQLite requires special handling for async
if settings.database_url.startswith("sqlite"):
    # Convert sqlite:/// to sqlite+aiosqlite:///
    async_url = settings.database_url.replace("sqlite://", "sqlite+aiosqlite://")
    engine = create_async_engine(
        async_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.log_level == "DEBUG"
    )
else:
    engine = create_async_engine(
        settings.database_url,
        echo=settings.log_level == "DEBUG"
    )

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Initialize database schema"""
    logger.info("Initializing database schema")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema initialized")


async def close_db():
    """Close database connections"""
    logger.info("Closing database connections")
    await engine.dispose()


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session as async context manager"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_session() -> AsyncSession:
    """Get database session for dependency injection"""
    async with get_db() as session:
        return session
