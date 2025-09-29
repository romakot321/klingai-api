from typing import Literal
from pydantic import BaseModel


class FalKlingGenerateImageToVideoRequest(BaseModel):
    prompt: str
    image_url: str
    tail_image_url: str | None = None
    duration: Literal["5", "10"] = "5"
    negative_prompt: str | None = None
    cfg_scale: float = 0.5


class FalKlingGenerateTextToVideoRequest(BaseModel):
    prompt: str
    aspect_ratio: Literal["9:16", "16:9", "1:1"]
    duration: Literal["5", "10"] = "5"
    negative_prompt: str | None = None
    cfg_scale: float = 0.5


class FalKlingGenerateElementsRequest(BaseModel):
    prompt: str
    input_image_urls: list[str]
    duration: Literal["5", "10"] = "5"
    aspect_ratio: Literal["9:16", "16:9", "1:1"] = "16:9"
    negative_prompt: str | None = None


class FalKlingGenerateVideoResponse(BaseModel):
    class Video(BaseModel):
        url: str

    video: Video
