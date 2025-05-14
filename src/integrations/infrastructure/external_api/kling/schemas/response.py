from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field, HttpUrl


class KlingTaskStatus(str, Enum):
    submitted = "submitted"
    processing = "processing"
    succeed = "succeed"
    failed = "failed"


class KlingResponseCode(int, Enum):
    authentication_failed = 1000
    authorization_is_empty = 1001
    authorization_is_invalid = 1002
    authorization_is_not_yet_valid = 1003
    authorization_expired = 1004
    account_exception = 1100
    insufficiend_balance = 1101
    resource_packages_expired = 1102
    unsufficient_permissions = 1103
    invalid_parameters = 1200
    invalid_key_or_value = 1201
    invalid_method = 1202
    resource_not_found = 1203
    internal_error = 5000
    temporarily_unavailable = 5001
    internal_timeout = 5002


class KlingResponseDataTaskInfo(BaseModel):
    external_task_id: str


class KlingResponseDataTaskResult(BaseModel):
    class Video(BaseModel):
        id: str
        url: HttpUrl
        duration: str

    videos: list[Video]


class KlingResponseDataSchema(BaseModel):
    task_id: str
    task_status: KlingTaskStatus
    task_status_msg: str | None = Field(default=None, description="Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)")
    task_info: KlingResponseDataTaskInfo | None = None
    created_at: int = Field(description="Unix timestamp, ms")
    updated_at: int = Field(description="Unix timestamp, ms")
    task_result: KlingResponseDataTaskResult | None = None


class KlingResponseSchema(BaseModel):
    code: int
    message: str
    request_id: str
    data: KlingResponseDataSchema
