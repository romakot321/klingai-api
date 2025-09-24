from pydantic import HttpUrl
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
            else:
                raise TypeError("Unknown task source")

        if self.source == TaskSource.kling:
            return KlingTaskToDomainMapper().map(task)

        raise TypeError("Unknown task source")

    @staticmethod
    def _set_task_source(tasks: list[TTaskResponse], source: TaskSource | None):
        if source:
            return source
        if tasks:
            if isinstance(tasks[0], KlingResponseSchema):
                return TaskSource.kling

        raise TypeError("Invalid tasks; source cannot be determined")


class TaskTextDTOToVideoRequestMapper:
    def __init__(self, task_source: TaskSource | None = None) -> None:
        self.source = task_source

    def map_one(self, task: TText2Video | dict) -> KlingGenerateTextToVideoParams:
        self.source = self._set_task_source([task], self.source)
        return self._map_task_to_domain(task)

    def _map_task_to_domain(self, task: TText2Video | dict) -> KlingGenerateTextToVideoParams:
        if isinstance(task, dict):
            if self.source == TaskSource.kling:
                task = TaskCreateFromTextDTO.model_validate(task)
            else:
                raise TypeError("Unknown task source")

        if self.source == TaskSource.kling:
            return TaskDTOToRequestMapper().map_text2video(task)

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

    def map_one(self, task: TImage2Video | dict) -> KlingGenerateImageToVideoParams:
        self.source = self._set_task_source([task], self.source)
        return self._map_task_to_domain(task)

    def _map_task_to_domain(self, task: TText2Video | dict) -> KlingGenerateImageToVideoParams:
        if isinstance(task, dict):
            if self.source == TaskSource.kling:
                task = TaskCreateFromImageDTO.model_validate(task)
            else:
                raise TypeError("Unknown task source")

        if self.source == TaskSource.kling:
            return TaskDTOToRequestMapper().map_image2video(task)

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

    def map_image2video(self, task: TaskCreateFromImageDTO) -> KlingGenerateImageToVideoParams:
        return KlingGenerateImageToVideoParams(**task.model_dump(mode="json", exclude_unset=True))

    def map_multiimage2video(self, task: TaskCreateFromMultiImageDTO) -> KlingGenerateMultiImageToVideoParams:
        return KlingGenerateMultiImageToVideoParams(**task.model_dump(mode="json", exclude_unset=True))



class KlingTaskToDomainMapper():
    def map(self, task: KlingResponseSchema) -> TaskExternalDTO:
        return TaskExternalDTO(
            external_id=task.data.task_id,
            status=task.data.task_status,
            error=task.data.task_status_msg,
            id=self._map_external_task_id(task.data.task_info.external_task_id) if task.data.task_info else None,
            result=self._map_task_result(task.data.task_result)
        )

    def _map_task_result(self, value: KlingResponseDataTaskResult | None) -> HttpUrl | None:
        if value is None or not value.videos:
            return None
        return value.videos[0].url

    def _map_external_task_id(self, value: str | None) -> int | None:
        if not value or not value.isdigit():
            return None
        return int(value)
