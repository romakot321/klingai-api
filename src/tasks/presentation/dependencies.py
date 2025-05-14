from typing import Annotated
from fastapi import Depends

from src.tasks.domain.interfaces.task_uow import ITaskUnitOfWork
from src.tasks.infrastructure.db.unit_of_work import PGTaskUnitOfWork
from src.tasks.infrastructure.http.api_client import TaskWebhookClientService


def get_task_uow() -> ITaskUnitOfWork:
    return PGTaskUnitOfWork()


def get_task_webhook_client() -> TaskWebhookClientService:
    return TaskWebhookClientService()


TaskUoWDepend = Annotated[ITaskUnitOfWork, Depends(get_task_uow)]
TaskWebhookClientServiceDepend = Annotated[TaskWebhookClientService, Depends(get_task_webhook_client)]
