from base64 import b64encode
import aiohttp
from enum import Enum
from typing import Literal
from urllib.parse import urljoin

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
        json = TaskEntityToDTOMapper().map_one(task)
        response = await self.client.post(url, json=json, headers=self.headers)
        response.raise_for_status()
        return response
