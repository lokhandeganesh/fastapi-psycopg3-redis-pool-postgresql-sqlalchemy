from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

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

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevents automatic expiration of objects after commit
    autocommit=False,  # Explicitly control when to commit transactions
    autoflush=False  # Avoids automatic flushes to the database, giving you control
)


# SQLAlchemy 2.0 Declarative Base
class Base(DeclarativeBase):
    pass


# FastAPI Dependency for Async DB Sessions
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
            