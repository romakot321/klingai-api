from enum import Enum
from pydantic import BaseModel, HttpUrl


class TaskSource(str, Enum):
    kling = 'kling'


class TaskStatus(str, Enum):
    submitted = "submitted"
    finished = "finished"
    failed = "failed"


class Task(BaseModel):
    id: int
    status: TaskStatus | None = None
    error: str | None = None
    user_id: str
    app_id: str
    result: str | None = None
    webhook_url: HttpUrl | None = None


class TaskCreate(BaseModel):
    user_id: str
    app_id: str
    prompt: str | None = None
    webhook_url: HttpUrl | None = None


class TaskUpdate(BaseModel):
    status: TaskStatus | None = None
    result: str | None = None
    error: str | None = None
    external_id: str | None = None
