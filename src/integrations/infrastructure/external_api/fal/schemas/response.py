from typing import Literal
from pydantic import BaseModel


class FalGenerateResponse(BaseModel):
    class Payload(BaseModel):
        class Video(BaseModel):
            url: str

        video: Video

    request_id: str
    status: Literal["OK", "ERROR", "IN_QUEUE"] | None = None
    error: str | None = None
    payload: Payload | None = None
