from pydantic import BaseModel


class CustomExceptionA(Exception):
    def __init__(self, message: str = "Something went wrong (A)"):
        self.message = message


class CustomExceptionB(Exception):
    def __init__(self, message: str = "Resource not found (B)"):
        self.message = message


class ErrorResponse(BaseModel):
    error_code: str
    message: str
