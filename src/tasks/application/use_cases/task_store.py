from io import BytesIO
from loguru import logger

from src.core.config import settings
from fastapi import HTTPException
from src.tasks.domain.entities import TaskStatus, TaskUpdate
from src.tasks.domain.interfaces.task_result_storage import ITaskStorageRepository
from src.tasks.domain.interfaces.task_source_client import ITaskSourceClient
from src.tasks.domain.interfaces.task_uow import ITaskUnitOfWork
from src.tasks.infrastructure.http.api_client import TaskWebhookClientService
from src.localstorage.domain.exceptions import FileNotFoundError


async def store_task_result(
        task_id: int,
        data: dict,
        uow: ITaskUnitOfWork,
        client: ITaskSourceClient,
        http_client: TaskWebhookClientService,
        storage: ITaskStorageRepository
):
    logger.info(f"Received task webhook: {data}")
    result = None
    try:
        result = await client.process_task_callback(data)
    except Exception as e:
        async with uow:
            await uow.tasks.update(task_id, TaskUpdate(result=str(task_id), status=TaskStatus.failed, error=str(e)))
            await uow.commit()
        logger.error(e)

    if result:
        storage.put_file(str(task_id), result)
        logger.info(f"Saved task #{task_id} result")

        async with uow:
            result = "https://" + settings.DOMAIN.rstrip("/") + "/result/" + str(task_id)
            await uow.tasks.update(task_id, TaskUpdate(result=result, status=TaskStatus.finished))
            await uow.commit()

    async with uow:
        task = await uow.tasks.get_by_pk(task_id)
    if task.status in (TaskStatus.finished, TaskStatus.failed):
        if task.webhook_url is not None:
            await http_client.send_webhook(str(task.webhook_url), task)


def get_task_result(task_id: int, storage: ITaskStorageRepository) -> BytesIO:
    try:
        return storage.read_file(str(task_id))
    except FileNotFoundError:
        raise HTTPException(404)
