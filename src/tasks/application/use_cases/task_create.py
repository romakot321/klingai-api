import logging

from src.tasks.domain.dtos import TaskCreateDTO
from src.tasks.domain.entities import Task, TaskCreate
from src.tasks.domain.interfaces.task_uow import ITaskUnitOfWork

logger = logging.getLogger(__name__)


async def create_task(task_data: TaskCreateDTO, uow: ITaskUnitOfWork) -> Task:
    request = TaskCreate(**task_data.model_dump(mode="json"))
    async with uow:
        new_task = await uow.tasks.create(request)
        logger.info(f"Created task #{new_task.id} with {request=}")
        await uow.commit()
    return new_task
