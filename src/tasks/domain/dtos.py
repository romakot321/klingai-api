from fastapi import Form
from pydantic import AliasChoices, BaseModel, Field, HttpUrl
from pydantic.json_schema import SkipJsonSchema


class TaskCreateDTO(BaseModel):
    app_id: str = Field(validation_alias=AliasChoices("appId", "app_id"))
    user_id: str = Field(validation_alias=AliasChoices("userId", "user_id"))
    prompt: str | None = None
    webhook_url: HttpUrl | None = None
    callback_url: SkipJsonSchema[str | None] = None


class TaskCreateFromTextDTO(TaskCreateDTO):
    prompt: str


class TaskCreateFromImageDTO(TaskCreateDTO):
    @classmethod
    def as_form(
        cls,
        appId: str = Form(),
        userId: str = Form(),
        prompt: str = Form(),
        webhook_url: HttpUrl | None = Form(None)
    ):
        return cls(app_id=appId, user_id=userId, prompt=prompt, webhook_url=webhook_url)


class TaskReadDTO(BaseModel):
    class Data(BaseModel):
        id: int
        status: int
        photo: HttpUrl | None = None
        result: HttpUrl | None = None

    error: bool
    messages: list[str]
    data: Data


class TaskExternalDTO(BaseModel):
    external_id: str
    id: int | None = None
    status: str
    error: str | None = None
    result: HttpUrl | None = None
