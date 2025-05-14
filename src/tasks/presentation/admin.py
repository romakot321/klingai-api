from sqladmin import ModelView

from src.tasks.infrastructure.db.orm import TaskDB


class TaskAdmin(ModelView, model=TaskDB):
    column_list = [TaskDB.id]
