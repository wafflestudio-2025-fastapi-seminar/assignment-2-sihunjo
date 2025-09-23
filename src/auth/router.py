
from fastapi import (
    APIRouter,
    Depends,
    Cookie,
    Response,
    status,
    HTTPException,
    Header
)
from typing import Annotated
from src.common import repository, security
from src.common.database import blocked_token_db, session_db, user_db
from src.auth.schemas import TokenResponse, TokenRequest
from datetime import datetime

auth_router = APIRouter(prefix="/auth", tags=["auth"])

SHORT_SESSION_LIFESPAN = 15
LONG_SESSION_LIFESPAN = 24 * 60

def verify_refresh_token(
    authorization: Annotated[str | None, Header()] = None,
) -> tuple[str, dict]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="BAD AUTHORIZATION HEADER")

    token = authorization.split(" ")[1]

    try:
        payload = security.verify_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID TOKEN")

    if repository.is_token_in_blacklist(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID TOKEN")
    
    return token, payload

@auth_router.post("/token",response_model=TokenResponse)
def issue_token(request: TokenRequest):
    user = repository.get_user_by_email(request.email)
    if not user or not security.verify_password(request.password, user["hashed_password"]):
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "INVALID ACCOUNT")
    access_token = security.create_access_token(data={"sub":str(user["user_id"])})
    refresh_token = security.create_refresh_token(data={"sub":str(user["user_id"])})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@auth_router.post("/token/refresh",response_model=TokenResponse)
def refresh_token(verified_data:tuple = Depends(verify_refresh_token)):
    old_refresh_token, payload = verified_data
    user_id = payload.get("sub")
    original_exp = datetime.fromtimestamp(payload.get("exp"))
    repository.add_token_to_blacklist(token=old_refresh_token, expires_at=original_exp)
    access_token = security.create_access_token(data={"sub": str(user_id)})
    refresh_token = security.create_refresh_token(data={"sub": str(user_id)})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)



@auth_router.delete("/token", status_code=status.HTTP_204_NO_CONTENT)
def invalidate_token(
    verified_data: tuple = Depends(verify_refresh_token)
):
    old_refresh_token, payload = verified_data
    original_exp = datetime.fromtimestamp(payload.get("exp"))
    
    repository.add_token_to_blacklist(
        token=old_refresh_token, 
        expires_at=original_exp
    )
    
    return None


@auth_router.post("/session")
def session_login(request:TokenRequest,response:Response):
    user = repository.get_user_by_email(request.email)
    if not user or not security.verify_password(request.password,user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="INVALID ACCOUNT")
    sid = repository.create_session_in_db(user["user_id"], LONG_SESSION_LIFESPAN)
    response.set_cookie(key="sid", value=sid, httponly=True, max_age=LONG_SESSION_LIFESPAN * 60)
    return {"message": "Session login successful"}

@auth_router.delete("/session")
def session_logout(response: Response, sid: Annotated[str | None, Cookie()] = None):
    if sid:
        repository.delete_session_from_db(sid)
        response.delete_cookie(key="sid")
    return response