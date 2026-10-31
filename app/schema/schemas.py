# from typing import Optional
import uuid

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    # phone_number: Optional[str] = None
    phone_number: str | None = None
    secret: str

class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    # created_at: datetime = current_datetime_local

    # Modern Pydantic v2 configuration format
    model_config = ConfigDict(from_attributes=True)


class UserInfoUpdate(BaseModel):
    phone_number: str
