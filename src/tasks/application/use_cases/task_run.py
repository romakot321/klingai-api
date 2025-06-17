from loguru import logger
import aiohttp

from src.tasks.domain.dtos import TaskExternalDTO
from src.tasks.domain.entities import Task, TaskStatus, TaskUpdate
from src.tasks.domain.interfaces.task_source_client import (
    ITaskSourceClient,
    TImage2Video,
    TTaskResult,
    TText2Video,
)
from src.tasks.domain.interfaces.task_uow import ITaskUnitOfWork


async def run_task_image2video(
    task_id: int,
    schema: TImage2Video,
    image: TTaskResult,
    image_tail: TTaskResult,
    client: ITaskSourceClient,
    uow: ITaskUnitOfWork,
) -> None:
    try:
        schema.external_task_id = str(task_id)
        task: TaskExternalDTO = await client.create_task_image2video(schema, image, image_tail)
    except aiohttp.ClientResponseError as e:
        if e.status == 429:  # Account exception, usually unsufficient balance
            logger.bind(name="balance").error(f"Unsufficient https://app.klingai.com balance: " + e.message)
        if e.status != 400:  # Unexpected params, but task still generating
            raise e
        task = None
    logger.info(f"Runned image2video task #{task_id}. External Response: {task}")
    async with uow:
        await uow.tasks.update(task_id, TaskUpdate(status=TaskStatus.submitted, external_id=task.external_id if task else None))
        await uow.commit()


async def run_task_text2video(
    task_id: int, schema: TText2Video, client: ITaskSourceClient, uow: ITaskUnitOfWork
) -> None:
    try:
        schema.external_task_id = str(task_id)
        task: TaskExternalDTO = await client.create_task_text2video(schema)
    except aiohttp.ClientResponseError as e:
        if e.status == 429:  # Account exception, usually unsufficient balance
            logger.bind(name="balance").error("Unsufficient https://app.klingai.com balance")
        if e.status != 400:  # Unexpected params, but task still generating
            raise e
        task = None
    logger.info(f"Runned text2video task #{task_id}. External Response: {task}")
    async with uow:
        await uow.tasks.update(task_id, TaskUpdate(status=TaskStatus.submitted, external_id=task.external_id if task else None))
        await uow.commit()
