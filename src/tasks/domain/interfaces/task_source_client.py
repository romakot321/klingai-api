import abc
from typing import Generic, TypeVar

from src.tasks.domain.dtos import TaskExternalDTO

TText2Video = TypeVar("TText2Video")
TImage2Video = TypeVar("TImage2Video")
TTaskResponse = TypeVar("TTaskResponse")
TTaskResult = TypeVar("TTaskResult")


class ITaskSourceClient(abc.ABC, Generic[TText2Video, TImage2Video, TTaskResponse, TTaskResult]):
    webhook_domain: str | None

    @abc.abstractmethod
    async def create_task_text2video(self, task_data: TText2Video) -> TaskExternalDTO: ...

    @abc.abstractmethod
    async def create_task_image2video(self, task_data: TImage2Video, image: TTaskResult) -> TaskExternalDTO: ...

    @abc.abstractmethod
    async def process_task_callback(self, data: dict) -> TTaskResult | None: ...
