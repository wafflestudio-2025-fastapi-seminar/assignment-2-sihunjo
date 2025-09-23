import re

from pydantic import BaseModel, field_validator, EmailStr, Field

from .errors import InvalidPasswordException

class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone_number: str = Field(pattern=r"^010-[0-9]{4}-[0-9]{4}$")
    bio: str | None = Field(default=None, max_length=500)
    height: float

    @field_validator('password', mode='after')
    def validate_password(cls, v):
        if len(v) < 8 or len(v) > 20:
            raise InvalidPasswordException()
        return v


class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    phone_number: str
    bio: str | None = None
    height: float