from pydantic import BaseModel, Field, field_validator
import re

class User(BaseModel):
    name: str
    id: int

class UserAge(BaseModel):
    name: str
    age: int

class FeedbackSimple(BaseModel):
    name: str
    message: str

class FeedbackValidated(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    message: str = Field(..., min_length=10, max_length=500)

    @field_validator("message")
    @classmethod
    def validate_no_bad_words(cls, value: str) -> str:
        bad_words = ["кринж", "рофл", "вайб"]
        lower_value = value.lower()
        for word in bad_words:
            if word in lower_value:
                raise ValueError("Использование недопустимых слов")
        return value