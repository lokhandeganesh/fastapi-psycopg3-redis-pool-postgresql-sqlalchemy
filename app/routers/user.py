import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Sqlalchemy imports
from app.core.database import get_db
from app.logger import logger
from app.model import models
from app.schema import schemas

router = APIRouter(prefix="/course_users", tags=['Course Users'])

@router.get("/{id}", response_model=schemas.UserOut)
async def get_course_user(id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    # Fetch User

    # stmt = select(models.UserJWT).where(models.UserJWT.id == id)
    # result = await db.execute(stmt)
    # user = result.scalar_one_or_none()

    #  Alternative approach using column targeting + mappings()
    stmt = select(models.UserJWT.id, models.UserJWT.email).where(models.UserJWT.id == id)
    result = await db.execute(stmt)
    
    # .mappings() transforms your selected columns into a dict format
    user = result.mappings().one_or_none()

    if not user:
        logger.error(f"user not for user-id:{id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id:{id} does not exist."
        )

    logger.info(f"user information retrieved for user-id:{id}")
    return user
