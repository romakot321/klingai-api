from typing import Literal
from pydantic import BaseModel, Field, HttpUrl


class KlingCameraControlConfigParams(BaseModel):
    """
    Contains 6 Fields, used to specify the camera’s movement or change in different directions

    When the camera movement Type is set to simple, the Required Field must be filled out; when other Types are specified, it should be left blank.
    Choose one out of the following six parameters, meaning only one parameter should be non-zero, while the rest should be zero.
    """

    horizontal: float | None = Field(default=None, ge=-10, le=10)
    vertical: float | None = Field(default=None, ge=-10, le=10)
    pan: float | None = Field(default=None, ge=-10, le=10)
    tilt: float | None = Field(default=None, ge=-10, le=10)
    roll: float | None = Field(default=None, ge=-10, le=10)
    zoom: float | None = Field(default=None, ge=-10, le=10)


class KlingCameraControlParams(BaseModel):
    config: KlingCameraControlConfigParams | None = None
    type: (
        Literal[
            "simple",
            "down_back",
            "forward_up",
            "right_turn_forward",
            "left_turn_forward",
        ]
        | None
    ) = Field(
        default=None,
        description="""
            simple: Camera movement，Under this Type, you can choose one out of six options for camera movement in the “config”.
            down_back: Camera descends and moves backward ➡️ Pan down and zoom out, Under this Type, the config parameter must be set to “None”.
            forward_up: Camera moves forward and tilts up ➡️ Zoom in and pan up, the config parameter must be set to “None”.
            right_turn_forward: Rotate right and move forward ➡️ Rotate right and advance, the config parameter must be set to “None”.
            left_turn_forward: Rotate left and move forward ➡️ Rotate left and advance, the config parameter must be set to “None”.
        """,
    )


class KlingGenerateTextToVideoParams(BaseModel):
    model_name: Literal["kling-v1", "kling-v1-6", "kling-v2-master"] = "kling-v1"
    prompt: str
    negative_prompt: str | None = None
    cfg_scale: float = Field(
        default=0.5,
        gt=0,
        lt=1,
        description="Flexibility in video generation; The higher the value, the lower the model’s degree of flexibility, and the stronger the relevance to the user’s prompt.",
    )
    mode: Literal["std", "pro"] = "std"
    aspect_ratio: Literal["16:9", "9:16", "1:1"] = "16:9"
    duration: Literal["5", "10"] = "5"
    callback_url: str | None = None
    external_task_id: str | None = None
    camera_control: KlingCameraControlParams | None = None


class KlingGenerateImageToVideoParams(BaseModel):
    model_name: Literal["kling-v1", "kling-v1-6", "kling-v2-master", "kling-v2-1", "kling-v2-1-master"] = "kling-v1"
    image: str | HttpUrl | None = Field(default=None, description="Can be passed as base64 string, without prefix")
    image_tail: str | HttpUrl | None = None
    prompt: str | None = Field(default=None, max_length=2500)
    negative_prompt: str | None = Field(default=None, max_length=2500)
    cfg_scale: float = Field(
        default=0.5,
        gt=0,
        lt=1,
        description="Flexibility in video generation; The higher the value, the lower the model’s degree of flexibility, and the stronger the relevance to the user’s prompt.",
    )
    mode: Literal["std", "pro"] = "std"
    static_mask: str | HttpUrl | None = None
    camera_control: KlingCameraControlParams | None = None
    duration: Literal["5", "10"] = "5"
    callback_url: str | None = None
    external_task_id: str | None = None

