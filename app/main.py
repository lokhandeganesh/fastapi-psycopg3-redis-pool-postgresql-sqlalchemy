from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI  #, HTTPException, status
from fastapi.responses import FileResponse
from fastapi_docshield import DocShield
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import engine, get_db
from app.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Test connection on startup
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1;"))
            logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

    yield

    # Clean up connection pool on shutdown
    await engine.dispose()
    logger.info("Database connection pool closed")


app = FastAPI(
    title="Fast API's project with new mechanism",
    lifespan=lifespan,
    root_path="/webservice",
    docs_url="/webservice/docs",
    redoc_url=None,
    openapi_url="/webservice/openapi.json",
    # makes curl show /webservice/...
    servers=[{"url": "/webservice"}],
    )


# Add protection to docs with multiple users
DocShield(
    app=app,
    credentials={
        "admin": settings.DOCSHIELD_ADMIN_PASS,
        "developer": settings.DOCSHIELD_DEVELOPER_PASS,
    }
)


@app.get("/")
def root():
    logger.info("Hi, Welcome to FastAPI application")    
    return {"message": "Hello World"}


favicon_path = r"app/static/favicon.ico"  # Adjust path to file


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)


@app.get("/health/db", include_in_schema=False)
async def db_health_check(db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Endpoint to test DB session checkout via get_db dependency
    """
    try:
        stmt = select(
            func.current_database().label("database"),
            func.version().label("database_version")
        )

        result = await db.execute(stmt)
        # convert result to a dict mapping
        db_info = result.mappings().first()

        return {
            "status": "online",
            "database": db_info["database"],
            "postgres_version": db_info["database_version"]
        }

        # result = await db.execute(text("SELECT current_database(), version();"))
        # db_info = result.fetchone()
        # return {
        #     "status": "online",
        #     "database": db_info[0],
        #     "postgres_version": db_info[1]
        # }

    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise
