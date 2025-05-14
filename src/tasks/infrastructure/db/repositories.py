from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.tasks.infrastructure.db.orm import TaskDB
from src.tasks.domain.entities import Task, TaskCreate, TaskStatus, TaskUpdate
from src.tasks.domain.interfaces.task_repository import ITaskRepository


class PGTaskRepository(ITaskRepository):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def create(self, task: TaskCreate) -> Task:
        model = TaskDB(**task.model_dump(mode="json"))
        self.session.add(model)

        try:
            await self.session.flush()
        except IntegrityError as e:
            try:
                detail = "Task can't be created. " + str(e)
            except IndexError:
                detail = "Task can't be created due to integrity error."
            raise HTTPException(409, detail=detail)

        return self._to_domain(model)

    async def get_by_pk(self, pk: int) -> Task:
        model: TaskDB | None = await self.session.get(TaskDB, pk)
        if model is None:
            raise HTTPException(404)
        return self._to_domain(model)

    async def update(self, pk: int, task: TaskUpdate) -> None:
        query = update(TaskDB).values(**task.model_dump(mode="json", exclude_none=True))
        await self.session.execute(query)
        try:
            await self.session.flush()
        except IntegrityError as e:
            try:
                detail = "Task can't be updated. " + str(e.orig).split('\nDETAIL:  ')[1]
            except IndexError:
                detail = "Task can't be updated due to integrity error."
            raise HTTPException(409, detail=detail)

    @staticmethod
    def _to_domain(model: TaskDB) -> Task:
        return Task(
            id=model.id,
            status=(TaskStatus(model.status) if model.status else None),
            user_id=model.user_id,
            app_id=model.app_id,
            result=model.result,
            error=model.error
        )
