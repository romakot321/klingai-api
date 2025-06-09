import asyncio
from loguru import logger
from socket import AF_INET

import aiohttp
from aiohttp.client import _RequestOptions

from src.integrations.infrastructure.http.interfaces import IAsyncHttpClient

SIZE_POOL_AIOHTTP = 100

class MockResponse:
    def __init__(self, text: str | None = None, status: int = 200, json: dict | None = None):
        self._text = text
        self._json = json
        self.status = status

    async def text(self):
        return self._text

    async def read(self):
        return b""

    async def json(self):
        return self._json

    def raise_for_status(self):
        if self.status // 100 != 2:
            raise ValueError("Mocked http error")

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self


class MockedAsyncHttpClient(IAsyncHttpClient[MockResponse]):
    aiohttp_client: aiohttp.ClientSession | None = None
    log = logger.bind(name="mocked http")

    @classmethod
    def get_aiohttp_client(cls) -> aiohttp.ClientSession:
        if cls.aiohttp_client is None:
            cls.log.debug("Initialize AiohttpClient session.")
            timeout = aiohttp.ClientTimeout(total=2)
            connector = aiohttp.TCPConnector(
                family=AF_INET,
                limit_per_host=SIZE_POOL_AIOHTTP,
            )
            cls.aiohttp_client = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
            )

        return cls.aiohttp_client

    @classmethod
    async def close_aiohttp_client(cls) -> None:
        if cls.aiohttp_client:
            cls.log.debug("Close AiohttpClient session.")
            await cls.aiohttp_client.close()
            cls.aiohttp_client = None

    @classmethod
    async def get(cls, url: str, **kwargs: _RequestOptions) -> MockResponse:
        return MockResponse()

    @classmethod
    async def post(cls, url: str, **kwargs: _RequestOptions) -> MockResponse:
        if url.endswith("/v1/videos/image2video") or url.endswith("/v1/videos/text2video"):
            return MockResponse(json={'code': 0, 'message': 'SUCCEED', 'request_id': 'CjikY2gHPbcAAAAABlkE-w', 'data': {'task_id': 'CjikY2gHPbcAAAAABlkE-w', 'task_status': 'submitted', 'created_at': 1747233384021, 'updated_at': 1747233384021}})
        return MockResponse(status=404)

    @classmethod
    async def put(cls, url: str, **kwargs: _RequestOptions) -> MockResponse:
        return MockResponse()

    @classmethod
    async def delete(cls, url: str, **kwargs: _RequestOptions) -> MockResponse:
        return MockResponse()

    @classmethod
    async def patch(cls, url: str, **kwargs: _RequestOptions) -> MockResponse:
        return MockResponse()
