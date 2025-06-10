"""All paths are the same as HailuoAPI for fotobudka compability"""

import io
from uuid import UUID
from fastapi import APIRouter, Body, Depends, File, Request, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import Response

from src.core.config import settings
from src.integrations.infrastructure.external_api.kling.adapter import KlingAdapter
from src.integrations.presentation.dependencies import get_kling_adapter
from src.localstorage.infrastructure.repository import LocalStorageRepository
from src.localstorage.presentation.dependencies import get_local_storage_repository
from src.tasks.application.use_cases.task_store import store_task_result
from src.tasks.domain.dtos import (
    TaskCreateDTO,
    TaskCreateFromImageDTO,
    TaskCreateFromTextDTO,
    TaskReadDTO,
)
from src.tasks.domain.mappers import TaskEntityToDTOMapper
from src.tasks.presentation.dependencies import TaskWebhookClientServiceDepend, TaskUoWDepend

from src.tasks.application.use_cases.task_create import create_task as uc_create_task
from src.tasks.application.use_cases.task_status import get_task as uc_get_task
from src.tasks.application.use_cases.task_store import get_task_result as uc_get_task_result
from src.tasks.application.use_cases.task_run import (
    run_task_image2video as uc_run_task_image2video,
)
from src.tasks.application.use_cases.task_run import (
    run_task_text2video as uc_run_task_text2video,
)

tasks_router = APIRouter()


@tasks_router.post("/generatetext", response_model=TaskReadDTO)
async def create_task_from_text(
    task_data: TaskCreateFromTextDTO,
    uow: TaskUoWDepend,
    task_source: KlingAdapter = Depends(get_kling_adapter),
):
    task = await uc_create_task(task_data, uow)
    task_data.callback_url = "https://" + settings.DOMAIN + "/webhook/" + str(task.id)
    await uc_run_task_text2video(task.id, task_data, task_source, uow)
    return TaskEntityToDTOMapper().map_one(task)


@tasks_router.post("/generate", response_model=TaskReadDTO)
async def create_task_from_image(
    uow: TaskUoWDepend,
#    image_tail: UploadFile | None = None,
    background_tasks: BackgroundTasks,
    task_source: KlingAdapter = Depends(get_kling_adapter),
    file: UploadFile = File(),
    task_data: TaskCreateFromImageDTO = Depends(TaskCreateFromImageDTO.as_form),
):
    task = await uc_create_task(task_data, uow)
    task_data.callback_url = "https://" + settings.DOMAIN + "/webhook/" + str(task.id)
    image = io.BytesIO(await file.read())
    #if image_tail is not None:
    #    image_tail = io.BytesIO(await image_tail.read())
    background_tasks.add_task(uc_run_task_image2video, task.id, task_data, image, None, task_source, uow)
    return TaskEntityToDTOMapper().map_one(task)


@tasks_router.get("/generation/{task_id}", response_model=TaskReadDTO)
async def get_task(task_id: int, uow: TaskUoWDepend):
    task = await uc_get_task(task_id, uow)
    return TaskEntityToDTOMapper().map_one(task)


@tasks_router.post("/webhook/{task_id}", include_in_schema=False)
async def task_result_webhook(
    task_id: int,
    uow: TaskUoWDepend,
    task_api_client: TaskWebhookClientServiceDepend,
    body: dict = Body(),
    storage: LocalStorageRepository = Depends(get_local_storage_repository),
    task_source: KlingAdapter = Depends(get_kling_adapter),
):
    try:
        await store_task_result(task_id, body, uow, task_source, task_api_client, storage)
    except HTTPException:
        pass


@tasks_router.get("/result/{task_id}", response_class=Response)
async def get_task_result(task_id: int, storage: LocalStorageRepository = Depends(get_local_storage_repository)):
    buffer = uc_get_task_result(task_id, storage)
    return Response(content=buffer.getvalue(), media_type="video/mp4")
