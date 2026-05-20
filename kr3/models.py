from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    username: str


class User(UserBase):
    password: str


class UserInDB(UserBase):
    hashed_password: str


class UserRegister(BaseModel):
    username: str
    password: str
    role: Optional[str] = "user"


class LoginData(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TodoCreate(BaseModel):
    title: str
    description: str


class TodoUpdate(BaseModel):
    title: str
    description: str
    completed: bool


class TodoItem(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
