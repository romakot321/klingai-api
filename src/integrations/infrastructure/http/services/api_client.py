from base64 import b64encode
import logging
import aiohttp
from enum import Enum
from typing import Literal
from urllib.parse import urljoin

from src.integrations.infrastructure.http.aiohttp_client import AiohttpClient
from src.integrations.infrastructure.http.interfaces import IAsyncHttpClient, TResponse

logger = logging.getLogger(__name__)


class AuthMixin:
    token: str | None

    @property
    def auth_headers(self):
        return {"Authorization": f'Bearer {self.token}'}


class APIClientService(AuthMixin):
    def __init__(
        self,
        client: IAsyncHttpClient[TResponse],
        source_url: str,
        headers: dict | None = None,
    ):
        self.client = client
        self.source_url = source_url
        self.headers = {**(headers or {}), **self.auth_headers}

    async def request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
        endpoint: str,
        json: dict | None = None,
        params: dict | None = None,
        headers: dict | None = None,
        **kwargs
    ) -> aiohttp.ClientResponse:
        headers = headers or {}
        request_params = {
            "url": urljoin(self.source_url, endpoint),
            "headers": {**self.headers, **headers},
            "json": json, "params": params, **kwargs
        }
        logger.debug(f"Perfoming api request to {endpoint} with {request_params=}")
        if method == "GET":
            response = await self.client.get(**request_params)
        elif method == "POST":
            response = await self.client.post(**request_params)
        elif method == "PUT":
            response = await self.client.put(**request_params)
        elif method == "DELETE":
            response = await self.client.delete(**request_params)
        elif method == "PATCH":
            response = await self.client.patch(**request_params)
        else:
            raise ValueError("Method not supported")
        if response.status != 200:
            logger.warning(f"Error occured on api request: {await response.text()}")
            response.raise_for_status()
        logger.debug(f"Get api response to {endpoint}: {response}")
        return response
