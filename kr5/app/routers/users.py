from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.schemas import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
def read_me(user: User = Depends(get_current_user)):
    return user


@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, _: User = Depends(get_current_user)):
    return User(id=user_id, role="user")
