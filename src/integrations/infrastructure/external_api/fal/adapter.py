import base64
import datetime as dt
import sys
import io
from loguru import logger
import time
import aiohttp
import jwt
import datetime
from pydantic import ValidationError

from src.integrations.infrastructure.external_api.fal.schemas.response import (
    FalGenerateResponse,
)
from src.integrations.infrastructure.external_api.kling.schemas.request import (
    KlingGenerateImageToVideoParams,
    KlingGenerateTextToVideoParams,
)
from src.integrations.infrastructure.external_api.kling.schemas.response import (
    KlingResponseDataSchema,
    KlingResponseSchema,
    KlingTaskStatus,
)
from src.integrations.infrastructure.external_api.mappers.task import (
    TaskDTOToFalKlingRequestMapper,
    TaskExternalToDomainMapper,
    TaskImageDTOToVideoRequestMapper,
    TaskTextDTOToVideoRequestMapper,
)
from src.integrations.infrastructure.http.aiohttp_client import AiohttpClient
from src.integrations.infrastructure.http.interfaces import IAsyncHttpClient
from src.integrations.infrastructure.http.services.api_client import APIClientService
from src.tasks.domain.dtos import (
    TaskCreateFromImageDTO,
    TaskCreateFromTextDTO,
    TaskExternalDTO,
)
from src.tasks.domain.entities import Task
from src.tasks.domain.interfaces.task_source_client import (
    ITaskSourceClient,
    TTaskResult,
)
from src.core.config import settings


class FalKlingAdapter(
    APIClientService,
    ITaskSourceClient[
        TaskCreateFromTextDTO, TaskCreateFromImageDTO, KlingResponseSchema, io.BytesIO
    ],
):
    token: str | None = settings.FAL_KEY
    log = logger.bind(name="kling")
    CDN_URL = "https://v3.fal.media"
    webhook_domain = settings.DOMAIN

    def __init__(
        self,
        client: IAsyncHttpClient = AiohttpClient,
        source_url: str = "https://queue.fal.run",
        headers: dict | None = None,
    ):
        super().__init__(client, source_url, headers)
        self._dto_mapper = TaskDTOToFalKlingRequestMapper()

    @property
    def auth_headers(self):
        return {"Authorization": f"Key {self.token}"}

    async def create_task_text2video(
        self, task_data: TaskCreateFromTextDTO
    ) -> TaskExternalDTO:
        request = self._dto_mapper.map_text2video(task_data)
        self.log.info(f"Text2video fal request: {request}")
        response: aiohttp.ClientResponse = await self.request(
            method="POST",
            endpoint="/fal-ai/kling-video/v2.1/master/text-to-video",
            headers={"Content-Type": "application/json"},
            json=request.model_dump(mode="json", exclude_none=True),
            params={
                "fal_webhook": f"https://{self.webhook_domain}/api/task/webhook/{task_data.external_task_id}"
            },
        )
        result = await response.json()
        self.log.debug(f"Text2video fal response: {result}")
        result = FalGenerateResponse.model_validate(result)
        return TaskExternalToDomainMapper().map_one(result)

    @staticmethod
    def _encode_image(image: io.BytesIO) -> str:
        return base64.b64encode(image.getvalue()).decode()

    async def upload_image(self, image: io.BytesIO) -> str:
        response = await self.request(
            "POST",
            self.CDN_URL + "/files/upload",
            data=image.read(),
            headers={"Content-Type": "image/jpeg"},
        )
        return (await response.json())["access_url"]

    async def create_task_image2video(
        self,
        task_data: TaskCreateFromImageDTO,
        image: io.BytesIO,
        image_tail: io.BytesIO | None,
    ) -> TaskExternalDTO:
        image_url = await self.upload_image(image)
        request = self._dto_mapper.map_image2video(task_data, image_url)
        self.log.info(f"image2video fal request: {request}")

        response = await self.request(
            method="POST",
            endpoint="/fal-ai/kling-video/v2.1/standard/image-to-video",
            headers={"Content-Type": "application/json"},
            json=request.model_dump(mode="json", exclude_none=True),
            params={
                "fal_webhook": f"https://{self.webhook_domain}/api/task/webhook/{task_data.external_task_id}"
            },
        )
        result = await response.json()
        self.log.debug(f"Image2video fal response: {result}")

        result = FalGenerateResponse.model_validate(result)
        return TaskExternalToDomainMapper().map_one(result)

    async def download_result(self, url: str) -> io.BytesIO:
        response = await self.request("GET", url)
        assert response.content_type.startswith("video/"), (
            f"Unexpected result content-type: {response.content_type}"
        )
        return io.BytesIO(await response.read())

    async def process_task_callback(self, data: dict) -> io.BytesIO | None:
        try:
            result = FalGenerateResponse.model_validate(data)
        except ValidationError as e:
            logger.error(e)
            return None

        if result.status != "OK" or result.payload is None:
            return None
        return await self.download_result(result.payload.video.url)
