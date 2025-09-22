from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Cookie,
    Header,
    status
)

from src.users.schemas import CreateUserRequest, UserResponse
from common.database import blocked_token_db, session_db, user_db
from src.users.errors import EmailAlreadyExists
from common import repository
from src.auth.dependencies import get_current_user

user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(request: CreateUserRequest) -> UserResponse:
    if repository.get_user_by_email(request.email):
        raise EmailAlreadyExists()
    
    new_user = repository.create_user_in_db(request)
    return UserResponse(**new_user)

@user_router.get("/me",response_model=UserResponse)
def get_user_info(current_user:dict=Depends(get_current_user)):
    return UserResponse(**current_user)