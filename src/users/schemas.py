import re

from pydantic import BaseModel, field_validator, EmailStr
from fastapi import HTTPException

from .errors import InvalidPasswordException

class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone_number: str
    bio: str | None = None
    height: float

    @field_validator('password', mode='after')
    def validate_password(cls, v):
        if len(v) < 8 or len(v) > 20:
            raise InvalidPasswordException()
        return v
    
    @field_validator('phone_number', mode='after')
    def validate_phone_number(cls, v):
        pattern = r"^010-[0-9]{4}-[0-9]{4}$"
        if not re.match(pattern,v):
            raise ValueError("전화번호 형식에 맞춰 입력하세요!")
        return v
        

    @field_validator('bio', mode='after')
    def validate_bio(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError("글자 수는 500자를 넘을 수 없습니다.")
        return v
    

    
class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    phone_number: str
    bio: str | None = None
    height: float