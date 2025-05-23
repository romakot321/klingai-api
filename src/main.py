from fastapi import FastAPI
import logging
from sqladmin import Admin
from prometheus_fastapi_instrumentator import Instrumentator

from src.core.config import settings
import src.core.logging_setup

from src.db.engine import engine
from src.tasks.presentation.admin import TaskAdmin
from src.tasks.presentation.api import tasks_router
from src.tasks.presentation.panel import router as tasks_panel_router

logger = logging.getLogger(__name__)


app = FastAPI(title=settings.PROJECT_NAME)

Instrumentator().instrument(app).expose(app, endpoint='/__internal_metrics__')

app.include_router(tasks_router, tags=["Task"])
app.include_router(tasks_panel_router, include_in_schema=False, prefix="/panel")


admin = Admin(app, engine)
admin.add_view(TaskAdmin)
