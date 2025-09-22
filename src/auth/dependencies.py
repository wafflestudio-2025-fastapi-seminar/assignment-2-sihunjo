from typing import Annotated

from fastapi import Cookie, Header, HTTPException, status
from jose import JWTError

from src.common import repository, security


def get_current_user(
    sid: Annotated[str | None, Cookie()] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> dict:
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        try:
            payload = security.verify_token(token)
            user = repository.get_user_by_id(int(payload.get("sub")))
            if user:
                return user
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID TOKEN")

    if sid:
        user_id = repository.get_user_id_from_session(sid)
        if user_id:
            user = repository.get_user_by_id(user_id)
            if user:
                return user
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID SESSION")

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="UNAUTHENTICATED")


