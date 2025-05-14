from typing import Annotated
from fastapi import Depends

from src.tasks.domain.interfaces.task_uow import ITaskUnitOfWork
from src.tasks.infrastructure.db.unit_of_work import PGTaskUnitOfWork
from src.tasks.infrastructure.http.api_client import TaskAPIClientService


def get_task_uow() -> ITaskUnitOfWork:
    return PGTaskUnitOfWork()


def get_task_api_client() -> TaskAPIClientService:
    return TaskAPIClientService()


TaskUoWDepend = Annotated[ITaskUnitOfWork, Depends(get_task_uow)]
TaskApiClientServiceDepend = Annotated[TaskAPIClientService, Depends(get_task_api_client)]
