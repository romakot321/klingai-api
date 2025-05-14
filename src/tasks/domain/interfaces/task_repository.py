import abc

from src.tasks.domain.entities import TaskCreate, TaskUpdate, Task


class ITaskRepository(abc.ABC):
    @abc.abstractmethod
    async def create(self, task: TaskCreate) -> Task: ...

    @abc.abstractmethod
    async def get_by_pk(self, pk: int) -> Task: ...

    @abc.abstractmethod
    async def update(self, pk: int, task: TaskUpdate) -> None: ...
