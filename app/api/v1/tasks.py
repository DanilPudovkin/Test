from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.enums import TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskListRead, TaskRead, TaskStatusRead
from app.services.task_service import TaskService, get_task_service

router = APIRouter()


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    session: AsyncSession = Depends(get_session),
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    return await service.create(session, payload)


@router.get("", response_model=TaskListRead)
async def list_tasks(
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    priority: TaskPriority | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
    service: TaskService = Depends(get_task_service),
) -> TaskListRead:
    return await service.list(session, status_filter, priority, limit, offset)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: UUID,
    session: AsyncSession = Depends(get_session),
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    return await service.get(session, task_id)


@router.delete("/{task_id}", response_model=TaskRead)
async def cancel_task(
    task_id: UUID,
    session: AsyncSession = Depends(get_session),
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    return await service.cancel(session, task_id)


@router.get("/{task_id}/status", response_model=TaskStatusRead)
async def get_task_status(
    task_id: UUID,
    session: AsyncSession = Depends(get_session),
    service: TaskService = Depends(get_task_service),
) -> TaskStatusRead:
    task = await service.get(session, task_id)
    return TaskStatusRead(id=task.id, status=task.status)
