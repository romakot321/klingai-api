from typing import Annotated
from fastapi import Depends

from src.integrations.infrastructure.external_api.fal.adapter import FalKlingAdapter
from src.integrations.infrastructure.http.aiohttp_client import AiohttpClient
from src.tasks.domain.interfaces.task_source_client import ITaskSourceClient
from src.tasks.domain.interfaces.task_uow import ITaskUnitOfWork
from src.tasks.infrastructure.db.unit_of_work import PGTaskUnitOfWork
from src.tasks.infrastructure.http.api_client import TaskWebhookClientService
from src.tasks.infrastructure.http.http_client import TaskAiohttpClient


def get_task_uow() -> ITaskUnitOfWork:
    return PGTaskUnitOfWork()


def get_task_webhook_client() -> TaskWebhookClientService:
    return TaskWebhookClientService(TaskAiohttpClient())


def get_task_source_client() -> ITaskSourceClient:
    return FalKlingAdapter(AiohttpClient())


TaskUoWDepend = Annotated[ITaskUnitOfWork, Depends(get_task_uow)]
TaskWebhookClientServiceDepend = Annotated[TaskWebhookClientService, Depends(get_task_webhook_client)]
