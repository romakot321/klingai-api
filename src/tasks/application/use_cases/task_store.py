from io import BytesIO
import logging

from fastapi import HTTPException
from src.tasks.domain.entities import TaskStatus, TaskUpdate
from src.tasks.domain.interfaces.http_client import IAsyncHttpClient
from src.tasks.domain.interfaces.task_result_storage import ITaskStorageRepository
from src.tasks.domain.interfaces.task_source_client import ITaskSourceClient, TTaskResult
from src.tasks.domain.interfaces.task_uow import ITaskUnitOfWork
from src.tasks.infrastructure.http.api_client import TaskWebhookClientService
from src.localstorage.domain.exceptions import FileNotFoundError

logger = logging.getLogger(__name__)


async def store_task_result(
        task_id: int,
        data: dict,
        uow: ITaskUnitOfWork,
        client: ITaskSourceClient,
        http_client: TaskWebhookClientService,
        storage: ITaskStorageRepository
):
    logger.info(f"Received task webhook: {data}")
    result = await client.process_task_callback(data)
    if result is None:
        raise HTTPException(422)

    storage.put_file(str(task_id), result)
    logger.info(f"Saved task #{task_id} result")

    async with uow:
        await uow.tasks.update(task_id, TaskUpdate(result=str(task_id)))
        await uow.commit()

    async with uow:
        task = await uow.tasks.get_by_pk(task_id)
        logger.warning((task_id, str(task.__dict__)))
        if task.webhook_url is not None:
            await http_client.send_webhook(str(task.webhook_url), task)


def get_task_result(task_id: int, storage: ITaskStorageRepository) -> BytesIO:
    try:
        return storage.read_file(str(task_id))
    except FileNotFoundError:
        raise HTTPException(404)
