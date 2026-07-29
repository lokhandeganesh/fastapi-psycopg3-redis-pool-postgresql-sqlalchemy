import uuid

from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    # created_at: datetime = current_datetime_local

    class Config:
        from_attributes = True
        