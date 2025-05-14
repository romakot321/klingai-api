from fastapi import FastAPI
import logging
from sqladmin import Admin
from prometheus_fastapi_instrumentator import Instrumentator

from src.core.config import settings
import src.core.logging_setup

from src.db.engine import engine
from src.tasks.presentation.admin import TaskAdmin
from src.tasks.presentation.api import tasks_router

logger = logging.getLogger(__name__)


app = FastAPI(title=settings.PROJECT_NAME)

Instrumentator().instrument(app).expose(app, endpoint='/__internal_metrics__')

app.include_router(tasks_router, tags=["Task"])


admin = Admin(app, engine)
admin.add_view(TaskAdmin)
