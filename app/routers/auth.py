from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.logger import logger
from app.model import models
from app.schema import schemas
from app.security import oauth2

# Implementing Argon2 password hashing
from app.util import utils

router = APIRouter(prefix="/auth", tags=["Authentication"])


# (Authentication routes can be added here in the future)
@router.post("/login", response_model=schemas.Token)
async def login(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    # then request form will return data in the form of
    #  {
    #   "username": "string",
    #   "password": "string"
    #  }

    # query the database to find user by email
    stmt = select(models.UserJWT).where(
        models.UserJWT.email == user_credentials.username
    )

    # Execute the query and fetch the user from the database
    result = await db.execute(stmt)

    # retrive the user
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(f"User Account does not exist: {user_credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
        )

    # check if password matches
    if not utils.verify_password(user.secret, user_credentials.password):
        logger.warning(f"Login failed for email: {user_credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )

    # Creating a JWT token
    # data that we want to include in the token
    data = {"sub": str(user.id)}

    # create access token with the data required
    access_token = oauth2.create_access_token(data=data)

    logger.info(f"User logged in with email: {user_credentials.username}")

    return {"access_token": access_token, "token_type": "bearer"}
