import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

# Sqlalchemy imports
from app.core.database import get_db
from app.logger import logger
from app.model import models
from app.schema import schemas

router = APIRouter(prefix="/course_users", tags=['Course Users'])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_course_user(user: schemas.UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    new_user = models.UserJWT(**user.model_dump())

    # add new_user to session
    db.add(new_user)

    try:
        # commit the transaction to the database
        await db.commit()
        # refresh the new_user object to get created in the database
        await db.refresh(new_user)

        logger.info(f"new user added to table with user-id: {new_user.id}")
        return new_user

    except IntegrityError as e:
        await db.rollback()
        logger.error(f"IntegrityError: {e.orig}")

        if "users_email_key" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create user due to data constraint"
        )


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
        logger.error(f"user not found for user-id:{id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id:{id} does not exist."
        )

    logger.info(f"user information retrieved for user-id:{id}")
    return user


@router.put("/{id}", response_model=schemas.UserOut)
async def update_user_info(id: uuid.UUID, user_info: schemas.UserInfoUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    # Update the user information
    update_data = user_info.model_dump(exclude_unset=True)

    # query to update user by id
    stmt = (
        update(models.UserJWT)
        .where(models.UserJWT.id == id)
        .values(**update_data)
        .returning(models.UserJWT)  # Tells postgres/sqlite to return the modified row
        )

    # Execute the update
    result = await db.execute(stmt)

    # retrive the user for updating
    user = result.scalar_one_or_none()

    if not user:
        logger.error(f"user not found for user-id:{id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id:{id} does not exist."
        )

    # commit the changes to the  database
    await db.commit()

    # Optional: refresh the object to ensure it has the latest DB state (e.g., updated_at triggers)
    await db.refresh(user)

    logger.info(f"User information updated for user-id: {id}")

    return user
