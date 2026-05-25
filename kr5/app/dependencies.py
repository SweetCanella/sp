from typing import Optional

from fastapi import Header, HTTPException, Depends

from app.schemas import User
from app.storage import TaskStorage, get_storage as _get_storage


def get_current_user(
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
    x_user_role: Optional[str] = Header(default="user", alias="X-User-Role"),
) -> User:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="X-User-Id header required")

    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="X-User-Id must be int")

    role = x_user_role or "user"
    return User(id=user_id, role=role)


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user


def get_storage() -> TaskStorage:
    return _get_storage()
