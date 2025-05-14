import abc
from typing import Generic, TypeVar

TResponse = TypeVar("TResponse")


class IAsyncHttpClient(abc.ABC, Generic[TResponse]):
    @classmethod
    @abc.abstractmethod
    async def get(cls, url: str, **kwargs) -> TResponse: ...

    @classmethod
    @abc.abstractmethod
    async def post(cls, url: str, **kwargs) -> TResponse: ...

    @classmethod
    @abc.abstractmethod
    async def put(cls, url: str, **kwargs) -> TResponse: ...

    @classmethod
    @abc.abstractmethod
    async def delete(cls, url: str, **kwargs) -> TResponse: ...

    @classmethod
    @abc.abstractmethod
    async def patch(cls, url: str, **kwargs) -> TResponse: ...
