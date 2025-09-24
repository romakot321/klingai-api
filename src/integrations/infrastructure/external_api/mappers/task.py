from pydantic import HttpUrl
from src.integrations.infrastructure.external_api.fal.schemas.request import FalKlingGenerateImageToVideoRequest, FalKlingGenerateTextToVideoRequest
from src.integrations.infrastructure.external_api.fal.schemas.response import FalGenerateResponse
from src.integrations.infrastructure.external_api.kling.schemas.request import KlingGenerateImageToVideoParams, KlingGenerateTextToVideoParams
from src.integrations.infrastructure.external_api.kling.schemas.response import KlingResponseDataTaskResult, KlingResponseSchema
from src.tasks.domain.dtos import TaskCreateFromImageDTO, TaskCreateFromTextDTO, TaskExternalDTO
from src.tasks.domain.entities import Task, TaskSource
from src.tasks.domain.interfaces.task_source_client import TImage2Video, TTaskResponse, TText2Video
from src.integrations.infrastructure.external_api.kling.schemas.request import KlingGenerateImageToVideoParams, \
    KlingGenerateTextToVideoParams, KlingGenerateMultiImageToVideoParams
from src.integrations.infrastructure.external_api.kling.schemas.response import KlingResponseDataTaskResult, \
    KlingResponseSchema
from src.tasks.domain.dtos import TaskCreateFromImageDTO, TaskCreateFromTextDTO, TaskExternalDTO, \
    TaskCreateFromMultiImageDTO

class TaskExternalToDomainMapper:
    def __init__(self, task_source: TaskSource | None = None) -> None:
        self.source = task_source

    def map_one(self, task: TTaskResponse | dict) -> TaskExternalDTO:
        self.source = self._set_task_source([task], self.source)
        return self._map_task_to_domain(task)

    def _map_task_to_domain(self, task: TTaskResponse | dict) -> TaskExternalDTO:
        if isinstance(task, dict):
            if self.source == TaskSource.kling:
                task = KlingResponseSchema.model_validate(task)
            elif self.source == TaskSource.fal:
                task = FalGenerateResponse.model_validate(task)
            else:
                raise TypeError("Unknown task source")

        if self.source == TaskSource.kling:
            return KlingTaskToDomainMapper().map(task)
        elif self.source == TaskSource.fal:
            return FalTaskToDomainMapper().map(task)

        raise TypeError("Unknown task source")

    @staticmethod
    def _set_task_source(tasks: list[TTaskResponse], source: TaskSource | None):
        if source:
            return source
        if tasks:
            if isinstance(tasks[0], KlingResponseSchema):
                return TaskSource.kling
            elif isinstance(tasks[0], FalGenerateResponse):
                return TaskSource.fal

        raise TypeError("Invalid tasks; source cannot be determined")


class TaskTextDTOToVideoRequestMapper:
    def __init__(self, task_source: TaskSource | None = None) -> None:
        self.source = task_source

    def map_one(self, task: TText2Video | dict) -> KlingGenerateTextToVideoParams:
        self.source = self._set_task_source([task], self.source)
        return self._map_task_to_domain(task)

    def _map_task_to_domain(self, task: TaskCreateFromTextDTO | dict) -> KlingGenerateTextToVideoParams:
        if isinstance(task, dict):
            if self.source == TaskSource.kling or self.source == TaskSource.fal:
                task = TaskCreateFromTextDTO.model_validate(task)
            else:
                raise TypeError("Unknown task source")

        if self.source == TaskSource.kling:
            return TaskDTOToRequestMapper().map_text2video(task)
        elif self.source == TaskSource.fal:
            return TaskDTOToRequestMapper().map_fal_text2video(task)

        raise TypeError("Unknown task source")

    @staticmethod
    def _set_task_source(tasks: list[TTaskResponse], source: TaskSource | None):
        if source:
            return source
        if tasks:
            if isinstance(tasks[0], TaskCreateFromTextDTO):
                return TaskSource.kling

        raise TypeError("Invalid tasks; source cannot be determined")


class TaskImageDTOToVideoRequestMapper:
    def __init__(self, task_source: TaskSource | None = None) -> None:
        self.source = task_source

    def map_one(self, task: TImage2Video | dict, image: str, image_tail: str | None = None) -> KlingGenerateImageToVideoParams:
        self.source = self._set_task_source([task], self.source)
        return self._map_task_to_domain(task, image, image_tail)

    def _map_task_to_domain(self, task: TaskCreateFromImageDTO | dict, image: str, image_tail: str | None = None) -> KlingGenerateImageToVideoParams:
        if isinstance(task, dict):
            if self.source == TaskSource.kling:
                task = TaskCreateFromImageDTO.model_validate(task)
            else:
                raise TypeError("Unknown task source")

        if self.source == TaskSource.kling:
            return TaskDTOToRequestMapper().map_image2video(task, image, image_tail)

        raise TypeError("Unknown task source")

    @staticmethod
    def _set_task_source(tasks: list[TTaskResponse], source: TaskSource | None):
        if source:
            return source
        if tasks:
            if isinstance(tasks[0], TaskCreateFromImageDTO):
                return TaskSource.kling

        raise TypeError("Invalid tasks; source cannot be determined")

class TaskMultiImageDTOToVideoRequestMapper:
    def __init__(self, task_source: TaskSource | None = None) -> None:
        self.source = task_source

    def map_one(self, task: TImage2Video | dict) -> KlingGenerateMultiImageToVideoParams:
        self.source = self._set_task_source([task], self.source)
        return self._map_task_to_domain(task)

    def _map_task_to_domain(self, task: TImage2Video | dict) -> KlingGenerateMultiImageToVideoParams:
        if isinstance(task, dict):
            if self.source == TaskSource.kling:
                task = TaskCreateFromMultiImageDTO.model_validate(task)
            else:
                raise TypeError("Unknown task source")

        if self.source == TaskSource.kling:
            return TaskDTOToRequestMapper().map_multiimage2video(task)

        raise TypeError("Unknown task source")

    @staticmethod
    def _set_task_source(tasks: list[TTaskResponse], source: TaskSource | None):
        if source:
            return source
        if tasks:
            if isinstance(tasks[0], TaskCreateFromMultiImageDTO):
                return TaskSource.kling

        raise TypeError("Invalid tasks; source cannot be determined")
        
class TaskDTOToRequestMapper():
    def map_text2video(self, task: TaskCreateFromTextDTO) -> KlingGenerateTextToVideoParams:
        return KlingGenerateTextToVideoParams(**task.model_dump(mode="json", exclude_unset=True))

    def map_image2video(self, task: TaskCreateFromImageDTO, image: str, image_tail: str | None) -> KlingGenerateImageToVideoParams:
        return KlingGenerateImageToVideoParams(**task.model_dump(mode="json", exclude_unset=True))

    def map_multiimage2video(self, task: TaskCreateFromMultiImageDTO) -> KlingGenerateMultiImageToVideoParams:
        return KlingGenerateMultiImageToVideoParams(**task.model_dump(mode="json", exclude_unset=True))



class TaskDTOToFalKlingRequestMapper():
    def map_image2video(self, task: TaskCreateFromImageDTO, image: str) -> FalKlingGenerateImageToVideoRequest:
        return FalKlingGenerateImageToVideoRequest(
            prompt=task.prompt or "Animate image",
            negative_prompt=task.negative_prompt,
            cfg_scale=task.cfg_scale,
            duration=task.duration,
            image_url=image
        )

    def map_text2video(self, task: TaskCreateFromTextDTO) -> FalKlingGenerateTextToVideoRequest:
        return FalKlingGenerateTextToVideoRequest(
            prompt=task.prompt,
            negative_prompt=task.negative_prompt,
            cfg_scale=task.cfg_scale,
            duration=task.duration,
            aspect_ratio=task.aspect_ratio
        )


class KlingTaskToDomainMapper():
    def map(self, task: KlingResponseSchema) -> TaskExternalDTO:
        return TaskExternalDTO(
            external_id=task.data.task_id,
            status=task.data.task_status,
            error=task.data.task_status_msg,
            id=self._map_external_task_id(task.data.task_info.external_task_id) if task.data.task_info else None,
            result=self._map_task_result(task.data.task_result)
        )

    def _map_task_result(self, value: KlingResponseDataTaskResult | None) -> str | None:
        if value is None or not value.videos:
            return None
        return str(value.videos[0].url)

    def _map_external_task_id(self, value: str | None) -> int | None:
        if not value or not value.isdigit():
            return None
        return int(value)


class FalTaskToDomainMapper():
    def map(self, task: FalGenerateResponse) -> TaskExternalDTO:
        return TaskExternalDTO(
            external_id=task.request_id,
            status=task.status or "SENDED",
            error=task.error,
            result=self._map_task_result(task.payload)
        )

    def _map_task_result(self, payload: FalGenerateResponse.Payload | None) -> str | None:
        if payload is None:
            return None
        return payload.video.url
