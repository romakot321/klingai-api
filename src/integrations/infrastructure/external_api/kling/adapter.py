import base64
import sys
import io
from loguru import logger
import time
import aiohttp
import jwt
import datetime
from pydantic import ValidationError

from src.integrations.infrastructure.external_api.kling.schemas.request import (
    KlingGenerateImageToVideoParams,
    KlingGenerateTextToVideoParams,
)
from src.integrations.infrastructure.external_api.kling.schemas.response import (
    KlingResponseDataSchema,
    KlingResponseSchema,
)
from src.integrations.infrastructure.external_api.mappers.task import (
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


class KlingAdapter(
    APIClientService,
    ITaskSourceClient[
        TaskCreateFromTextDTO, TaskCreateFromImageDTO, KlingResponseSchema, io.BytesIO
    ],
):
    _token: str | None = None
    log = logger.bind(name="kling")
    _token_issue_at: datetime.datetime | None = None

    def __init__(
        self,
        client: IAsyncHttpClient = AiohttpClient,
        source_url: str = "https://api.klingai.com",
        headers: dict | None = None,
    ):
        super().__init__(client, source_url, headers)
        self._token = None
        self._txtdto_mapper = TaskTextDTOToVideoRequestMapper()
        self._imgdto_mapper = TaskImageDTOToVideoRequestMapper()

    @staticmethod
    def _generate_token(access_key: str, secret_key: str) -> str:
        headers = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "iss": access_key,
            "exp": int(time.time())
            + 1800,  # The valid time, in this example, represents the current time+1800s(30min)
            "nbf": int(time.time())
            - 5,  # The time when it starts to take effect, in this example, represents the current time minus 5s
        }
        token = jwt.encode(payload, secret_key, headers=headers)
        return token

    @property
    def token(self):
        if (
            self._token is None
            or self._token_issue_at is None
            or (datetime.datetime.now() - self._token_issue_at).seconds > 1700
        ):
            self._token = self._generate_token(
                settings.KLING_ACCESS_KEY, settings.KLING_SECRET_KEY
            )
            self._token_issue_at = datetime.datetime.now()
        return self._token

    async def create_task_text2video(
        self, task_data: TaskCreateFromTextDTO
    ) -> TaskExternalDTO:
        request = self._txtdto_mapper.map_one(task_data)
        response: aiohttp.ClientResponse = await self.request(
            method="POST",
            endpoint="/v1/videos/text2video",
            headers={"Content-Type": "application/json"},
            json=request.model_dump(mode="json", exclude_none=True),
        )
        result = await response.json()
        self.log.debug(f"Text2video kling response: {result}")
        result = KlingResponseSchema.model_validate(result)
        return TaskExternalToDomainMapper().map_one(result)

    @staticmethod
    def _encode_image(image: io.BytesIO) -> str:
        return base64.b64encode(image.getvalue()).decode()

    async def create_task_image2video(
        self, task_data: TaskCreateFromImageDTO, image: io.BytesIO, image_tail: io.BytesIO | None
    ) -> TaskExternalDTO:
        request = self._imgdto_mapper.map_one(task_data)
        request.camera_control = None
        self.log.info(f"image2video request: {request}")
        request.image = self._encode_image(image)
        if image_tail:
            request.image_tail = self._encode_image(image_tail)
        response = await self.request(
            method="POST",
            endpoint="/v1/videos/image2video",
            headers={"Content-Type": "application/json"},
            json=request.model_dump(mode="json", exclude_none=True),
        )
        result = await response.json()
        self.log.debug(f"Image2video kling response: {result}")
        result = KlingResponseSchema.model_validate(result)
        return TaskExternalToDomainMapper().map_one(result)

    async def process_task_callback(self, data: dict) -> io.BytesIO | None:
        try:
            task_data = KlingResponseDataSchema.model_validate(data)
        except ValidationError:
            return None
        if task_data.task_status == "failed":
            raise ValueError(f"Generation failed: {task_data.task_status_msg}")
        elif task_data.task_status != "succeed" or task_data.task_result is None or not task_data.task_result.videos:
            return None

        response = await self.client.get(str(task_data.task_result.videos[0].url))
        response.raise_for_status()

        result = io.BytesIO(await response.read())
        return result

    async def get_limits(self) -> dict:
        response = await self.request(
            method="GET",
            endpoint="/account/costs",
            headers={"Content-Type": "application/json"},
            params={"start_time": (datetime.datetime.now() - datetime.timedelta(days=30)).timestamp(), "end_time": datetime.datetime.now().timestamp()}
        )
        return response


async def print_kling_remaining_limits():
    adapter = KlingAdapter()
    print(await adapter.get_limits())


if __name__ == "__main__":
    import asyncio
    asyncio.run(print_kling_remaining_limits())
