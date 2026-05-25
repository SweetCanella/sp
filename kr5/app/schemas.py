from typing import Optional, Literal

from pydantic import BaseModel, Field

TaskStatus = Literal["todo", "in_progress", "done"]


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=80)
    description: Optional[str] = None
    status: TaskStatus = "todo"
    priority: int = Field(ge=1, le=5)


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: int
    owner_id: int


class StatusUpdate(BaseModel):
    status: TaskStatus


class User(BaseModel):
    id: int
    role: str
