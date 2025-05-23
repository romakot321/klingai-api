from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.tasks.application.use_cases.task_status import get_task
from src.tasks.domain.entities import TaskStatus
from src.tasks.presentation.dependencies import TaskUoWDepend


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("", response_class=RedirectResponse)
async def index(request: Request):
    return RedirectResponse(url="/panel/image2video")


@router.get("/text2video", response_class=HTMLResponse)
async def text2video_page(request: Request):
    return templates.TemplateResponse("text2video.html", {"request": request})


@router.get("/image2video", response_class=HTMLResponse)
async def image2video_page(request: Request):
    return templates.TemplateResponse("image2video.html", {"request": request})


@router.get("/task/{task_id}", response_class=HTMLResponse)
async def task_page(request: Request, task_id: int, uow: TaskUoWDepend):
    task = await get_task(task_id, uow)
    if task.status == TaskStatus.failed:
        return templates.TemplateResponse("task_failed.html", {"request": request, "message": task.error})
    elif task.status != TaskStatus.finished:
        return templates.TemplateResponse("task_processing.html", {"request": request})
    elif task.status == TaskStatus.finished:
        return templates.TemplateResponse("task_finished.html", {"request": request, "result_url": task.result})
