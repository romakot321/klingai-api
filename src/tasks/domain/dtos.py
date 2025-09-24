from typing import Literal
from fastapi import Depends, Form
from pydantic import AliasChoices, BaseModel, Field, HttpUrl
from pydantic.json_schema import SkipJsonSchema


class TaskCreateDTO(BaseModel):
    app_id: str = Field(validation_alias=AliasChoices("appId", "app_id"))
    user_id: str = Field(validation_alias=AliasChoices("userId", "user_id"))
    prompt: str | None = None
    webhook_url: HttpUrl | None = None
    callback_url: SkipJsonSchema[str | None] = None


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

    @classmethod
    def as_form(
        cls,
        horizontal: float | None = Form(None),
        vertical: float | None = Form(None),
        pan: float | None = Form(None),
        tilt: float | None = Form(None),
        roll: float | None = Form(None),
        zoom: float | None = Form(None),
    ):
        return cls(
            horizontal=horizontal,
            vertical=vertical,
            pan=pan,
            tilt=tilt,
            roll=roll,
            zoom=zoom,
        )


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

    @classmethod
    def as_form(
        cls,
        config: KlingCameraControlConfigParams | None = Depends(
            KlingCameraControlConfigParams.as_form
        ),
        camera_type: Literal[
            "simple",
            "down_back",
            "forward_up",
            "right_turn_forward",
            "left_turn_forward",
        ]
        | None = Form(None),
    ):
        return cls(config=config, type=camera_type)


class TaskCreateFromTextDTO(TaskCreateDTO):
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


class TaskCreateFromImageDTO(TaskCreateDTO):
    model_name: Literal["kling-v1", "kling-v1-6", "kling-v2-master", "kling-v2-1", "kling-v2-1-master"] = "kling-v1"
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

    @classmethod
    def as_form(
        cls,
        model_name: Literal["kling-v1", "kling-v1-6", "kling-v2-master", "kling-v2-1", "kling-v2-1-master"] = Form(),
        prompt: str | None = Form(default=None, max_length=2500),
        negative_prompt: str | None = Form(default=None, max_length=2500),
        cfg_scale: float = Form(gt=0, lt=1),
        mode: str = Form(default="std"),
        duration: str = Form(default="5"),
        # callback_url: str = Form(default=None),
        webhook_url: str | None = Form(default=None),
        camera_control: KlingCameraControlParams = Depends(
            KlingCameraControlParams.as_form
        ),
        user_id: str = Form(),
        app_id: str = Form()
    ):
        return cls(
            model_name=model_name,
            prompt=prompt,
            negative_prompt=negative_prompt,
            cfg_scale=cfg_scale,
            mode=mode,
            duration=duration,
            webhook_url=webhook_url,
            camera_control=camera_control,
            app_id=app_id,
            user_id=user_id
        )

class TaskCreateFromMultiImageDTO(TaskCreateDTO):
    model_name: Literal["kling-v1-6"] = "kling-v1-6"
    image_list: list[dict[str, str]] = Field(..., description="Reference Image List, up to 4 images")
    prompt: str | None = Field(default=None, max_length=2500)
    negative_prompt: str | None = Field(default=None, max_length=2500)
    cfg_scale: float = Field(
        default=0.5,
        gt=0,
        lt=1,
        description="Flexibility in video generation; The higher the value, the lower the model's degree of flexibility, and the stronger the relevance to the user's prompt.",
    )
    mode: Literal["std", "pro"] = "std"
    duration: Literal["5", "10"] = "5"
    aspect_ratio: Literal["16:9", "9:16", "1:1"] = "16:9"
    callback_url: str | None = None
    external_task_id: str | None = None

    @classmethod
    def as_form(
            cls,
            model_name: Literal["kling-v1-6"] = Form(),
            prompt: str | None = Form(default=None, max_length=2500),
            negative_prompt: str | None = Form(default=None, max_length=2500),
            cfg_scale: float = Form(gt=0, lt=1),
            mode: str = Form(default="std"),
            duration: str = Form(default="5"),
            aspect_ratio: str = Form(default="16:9"),
            webhook_url: str | None = Form(default=None),
            user_id: str = Form(),
            app_id: str = Form(),
    ):
        return cls(
            model_name=model_name,
            prompt=prompt,
            negative_prompt=negative_prompt,
            cfg_scale=cfg_scale,
            mode=mode,
            duration=duration,
            aspect_ratio=aspect_ratio,
            webhook_url=webhook_url,
            app_id=app_id,
            user_id=user_id,
            image_list=[],
        )
        
class TaskReadDTO(BaseModel):
    class Data(BaseModel):
        id: int
        status: int
        photo: str | None = None
        result: str | None = None

    error: bool
    messages: list[str]
    data: Data


class TaskExternalDTO(BaseModel):
    external_id: str
    id: int | None = None
    status: str
    error: str | None = None
    result: str | None = None
