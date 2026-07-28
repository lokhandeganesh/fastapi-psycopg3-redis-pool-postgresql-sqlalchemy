from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi_docshield import DocShield

from app.core.config import settings
from app.logger import logger

app = FastAPI(
    title="Fast API's project with new mechanism",
    # lifespan=lifespan,
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
