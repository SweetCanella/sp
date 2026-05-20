from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserValidate(BaseModel):
    username: str
    age: int = Field(gt=18)
    email: EmailStr
    password: str = Field(min_length=8, max_length=16)
    phone: Optional[str] = "Unknown"


class UserIn(BaseModel):
    username: str
    age: int


class UserOut(BaseModel):
    id: int
    username: str
    age: int
