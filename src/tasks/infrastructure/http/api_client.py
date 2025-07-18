import aiohttp
from loguru import logger

from src.tasks.domain.entities import Task
from src.tasks.domain.interfaces.http_client import IAsyncHttpClient, TResponse
from src.tasks.domain.mappers import TaskEntityToDTOMapper
from src.tasks.infrastructure.http.http_client import TaskAiohttpClient


class TaskWebhookClientService:
    def __init__(
        self,
        client: IAsyncHttpClient[TResponse] = TaskAiohttpClient,
        headers: dict | None = None,
    ):
        self.client = client
        self.headers = headers or {}

    async def send_webhook(self, url: str, task: Task) -> aiohttp.ClientResponse:
        data = TaskEntityToDTOMapper().map_one(task)
        response = await self.client.post(url, json=data.model_dump(), headers=self.headers)
        logger.info(f"Sended webhook for task #{task.id}. Response: {response}")
        return response
