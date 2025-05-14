from fastapi import FastAPI
from sqladmin import Admin

from src.core.config import settings

from src.db.engine import engine
from src.tasks.presentation.admin import TaskAdmin
from src.tasks.presentation.api import tasks_router


app = FastAPI(title=settings.PROJECT_NAME)


app.include_router(tasks_router, tags=["Task"])

admin = Admin(app, engine)
admin.add_view(TaskAdmin)
