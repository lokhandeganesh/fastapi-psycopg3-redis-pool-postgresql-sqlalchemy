from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.base import Base
from app.core.config import settings
from app.logger import logger

# Import your models inside the function so SQLAlchemy registers them
from app.model import models

# Async Engine with psycopg3 & connection pool
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True if you want to inspect SQL queries in dev
    pool_size=10,  # Core persistent connections
    max_overflow=10,  # Additional temporary connections during high load spikes
    pool_timeout=30,  # Seconds to wait for an available connection before timing out
    pool_recycle=1800,  # Recycle connections every 30 minutes to drop stale sockets
    pool_pre_ping=True  # Validate connections health before handing it out from pool
    )

#  async code into a function to be called at startup
async def init_db() -> None:
    """Initialize database schemas and extensions"""
    logger.info("Initializing database schemas...")
    try:
        async with engine.begin() as conn:
            # must await conn.execute in async mode
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS course"))
            logger.info("Schema 'course' verified/created successfully.")

            # Create all tables asynchronously using run_sync
            await conn.run_sync(models.Base.metadata.create_all)
            logger.info("Database tables initialized successfully.")
    except Exception:
        logger.error("Database initialization failed", exc_info=True)
        raise


# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevents automatic expiration of objects after commit
    autocommit=False,  # Explicitly control when to commit transactions
    autoflush=False  # Avoids automatic flushes to the database, giving you control
)


# FastAPI Dependency for Async DB Sessions
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
