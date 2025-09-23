from .database import user_db, session_db, blocked_token_db, get_new_user_id
from .security import hash_password


def get_user_by_email(email: str) -> dict | None:
    for user in user_db:
        if user["email"] == email:
            return user
    return None


def get_user_by_id(user_id: int) -> dict | None:
    for user in user_db:
        if user["user_id"] == user_id:
            return user
    return None


def create_user_in_db(request) -> dict:
    from src.users.schemas import CreateUserRequest  # type: ignore

    # Defensive unique email check at data layer (simulates DB UNIQUE constraint)
    if get_user_by_email(request.email):
        from src.users.errors import EmailAlreadyExists  # type: ignore
        raise EmailAlreadyExists()

    hashed_password = hash_password(request.password)
    new_user = {
        "user_id": get_new_user_id(),
        "email": request.email,
        "hashed_password": hashed_password,
        "name": request.name,
        "phone_number": request.phone_number,
        "height": request.height,
        "bio": request.bio,
    }
    user_db.append(new_user)
    return new_user


import uuid
from datetime import datetime, timedelta, timezone


def get_user_id_from_session(sid: str) -> int | None:
    session = session_db.get(sid)
    if session and session["expires_at"] > datetime.now(timezone.utc):
        return session["user_id"]
    return None


def create_session_in_db(user_id: int, expire_in_minutes: int) -> str:
    sid = str(uuid.uuid4())

    expires_time = datetime.now(timezone.utc) + timedelta(minutes=expire_in_minutes)
    session_db[sid] = {
        "user_id": user_id,
        "expires_at": expires_time,
    }
    return sid


def delete_session_from_db(sid: str) -> None:
    if sid in session_db:
        del session_db[sid]


def add_token_to_blacklist(token: str, expires_at: datetime):
    blocked_token_db[token] = expires_at  # type: ignore[index]


def is_token_in_blacklist(token: str) -> bool:
    return token in blocked_token_db


