from pydantic import BaseModel, EmailStr, Field

class UserShema(BaseModel):
    username: str = Field(min_length=3, max_length=25)
    email: str = EmailStr
    password: str = Field(min_length=8)
    
    
class UserResponse(BaseModel):
    id: int = Field(primary_key=True, default=1)
    username: str
    email: str
    
    class Config:
        from_attributes = True


class TokenShema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer" 


class RequestEmail(BaseModel):
    email: EmailStr