from uuid import UUID

from src.core.config import settings
from src.tasks.domain.dtos import TaskReadDTO
from src.tasks.domain.entities import Task
from src.tasks.domain.interfaces.task_uow import ITaskUnitOfWork
from src.tasks.domain.mappers import TaskEntityToDTOMapper


async def get_task(task_pk: int, uow: ITaskUnitOfWork) -> Task:
    async with uow:
        task = await uow.tasks.get_by_pk(task_pk)
    if task.result and not task.result.startswith("http"):
        task.result = "https://" + settings.DOMAIN.rstrip("/") + "/result/" + task.result.lstrip()
    return task
