from src.tasks.domain.dtos import TaskReadDTO
from src.tasks.domain.entities import Task, TaskStatus


class TaskEntityToDTOMapper:
    def map_one(self, task: Task | dict) -> TaskReadDTO:
        if isinstance(task, dict):
            task = Task.model_validate(task)
        return TaskReadDTO(
            error=True if task.error else False,
            messages=[task.error] if task.error else [],
            data=TaskReadDTO.Data(
                id=task.id,
                status=self._map_task_status(task.status),
                photo=None,
                result=task.result
            )
        )

    def _map_task_status(self, status: TaskStatus | None) -> int:
        if status is None:
            return 0
        if status == TaskStatus.submitted:
            return 1
        if status == TaskStatus.finished:
            return 3
        if status == TaskStatus.failed:
            return 4
