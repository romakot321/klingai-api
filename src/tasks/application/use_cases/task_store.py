from io import BytesIO

from fastapi import HTTPException
from src.tasks.domain.entities import TaskStatus, TaskUpdate
from src.tasks.domain.interfaces.http_client import IAsyncHttpClient
from src.tasks.domain.interfaces.task_result_storage import ITaskStorageRepository
from src.tasks.domain.interfaces.task_source_client import ITaskSourceClient, TTaskResult
from src.tasks.domain.interfaces.task_uow import ITaskUnitOfWork
from src.tasks.infrastructure.http.api_client import TaskAPIClientService
from src.localstorage.domain.exceptions import FileNotFoundError


async def store_task_result(
        task_id: int,
        data: dict,
        uow: ITaskUnitOfWork,
        client: ITaskSourceClient,
        http_client: TaskAPIClientService,
        storage: ITaskStorageRepository
):
    result = await client.process_task_callback(data)
    if result is None:
        raise HTTPException(422)

    storage.put_file(str(task_id), result)

    async with uow:
        await uow.tasks.update(task_id, TaskUpdate(result=str(task_id)))
        await uow.commit()

        task = await uow.tasks.get_by_pk(task_id)
        if task.webhook_url is not None:
            await http_client.send_webhook(str(task.webhook_url), task)


def get_task_result(task_id: int, storage: ITaskStorageRepository) -> BytesIO:
    try:
        return storage.read_file(str(task_id))
    except FileNotFoundError:
        raise HTTPException(404)
