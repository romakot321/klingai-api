from src.integrations.infrastructure.external_api.kling.adapter import KlingAdapter
from src.integrations.infrastructure.external_api.kling.mocked_client import MockedAsyncHttpClient


def get_kling_adapter() -> KlingAdapter:
    # return KlingAdapter(client=MockedAsyncHttpClient())
    return KlingAdapter()
