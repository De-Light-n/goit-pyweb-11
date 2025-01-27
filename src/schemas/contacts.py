from datetime import datetime
from pydantic import BaseModel, Field

from src.schemas.users import UserResponse


class ContactShema(BaseModel):
    name: str = Field(min_length=3, max_length=25)
    surname: str = Field(min_length=3, max_length=25)
    email: str = Field(min_length=8)
    phone_number: str = Field(min_length=10, max_length=20)
    birthdate: datetime = Field(default=datetime.date(datetime.today()))

class ContactResponse(ContactShema):
    id: int = Field(default=1, ge=1)
    created_at: datetime = Field(default_factory=datetime.now)
    user: UserResponse | None
    
    
    class Config:
        from_attributes = True