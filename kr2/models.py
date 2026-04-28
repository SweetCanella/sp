from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Имя пользователя")
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', description="Email пользователя")
    age: Optional[int] = Field(None, ge=1, le=150, description="Возраст (от 1 до 150)")
    is_subscribed: Optional[bool] = Field(False, description="Подписка на рассылку")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Alice",
                "email": "alice@example.com",
                "age": 30,
                "is_subscribed": True
            }
        }
    }


class LoginData(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class ProfileResponse(BaseModel):
    username: str
    message: str


class CommonHeaders(BaseModel):
    user_agent: str = Field(..., alias="User-Agent", description="User-Agent заголовок")
    accept_language: str = Field(..., alias="Accept-Language", description="Accept-Language заголовок")
    
    @field_validator("accept_language")
    @classmethod
    def validate_accept_language(cls, value: str) -> str:
        if not value:
            raise ValueError("Accept-Language header cannot be empty")
        
        if not re.match(r'^[a-zA-Z\-*,\s;=0-9.]+$', value):
            raise ValueError('Invalid Accept-Language format. Expected format like: "en-US,en;q=0.9,es;q=0.8"')
        
        parts = value.split(',')
        for part in parts:
            part = part.strip()
            if ';q=' in part:
                lang, q = part.split(';q=')
                if not re.match(r'^[a-zA-Z\-*]+$', lang.strip()):
                    raise ValueError(f'Invalid language tag: {lang}')
                try:
                    q_value = float(q)
                    if not (0 <= q_value <= 1):
                        raise ValueError(f'Quality value must be between 0 and 1, got: {q_value}')
                except ValueError:
                    raise ValueError(f'Invalid quality value: {q}')
            else:
                if part and not re.match(r'^[a-zA-Z\-*]+$', part):
                    raise ValueError(f'Invalid language tag: {part}')
        
        return value
    
    @field_validator("user_agent")
    @classmethod
    def validate_user_agent(cls, value: str) -> str:
        if not value:
            raise ValueError("User-Agent header cannot be empty")
        return value
    
    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept-Language": "en-US,en;q=0.9,es;q=0.8"
            }
        }
    }