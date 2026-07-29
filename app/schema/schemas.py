import uuid

from pydantic import BaseModel, ConfigDict, EmailStr


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    # created_at: datetime = current_datetime_local
    
    # Modern Pydantic v2 configuration format
    model_config = ConfigDict(from_attributes=True)
        