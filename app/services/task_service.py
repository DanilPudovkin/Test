from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.messaging.producer import TaskProducer
from app.models.enums import TaskPriority, TaskStatus
from app.models.task import Task
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskListRead


class TaskService:
    def __init__(self, repository: TaskRepository, producer: TaskProducer) -> None:
        self.repository = repository
        self.producer = producer

    async def create(self, session: AsyncSession, payload: TaskCreate) -> Task:
        task = Task(
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
            status=TaskStatus.PENDING,
        )
        task = await self.repository.create(session, task)
        try:
            await self.producer.publish_task(task.id, task.priority)
        except Exception as exc:
            task.status = TaskStatus.FAILED
            task.finished_at = datetime.now(UTC)
            task.error = "Failed to enqueue task"
            await self.repository.save(session, task)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Task queue is unavailable",
            ) from exc
        return task

    async def list(
        self,
        session: AsyncSession,
        status_filter: TaskStatus | None,
        priority: TaskPriority | None,
        limit: int,
        offset: int,
    ) -> TaskListRead:
        items = await self.repository.list(session, status_filter, priority, limit, offset)
        total = await self.repository.count(session, status_filter, priority)
        return TaskListRead(items=items, total=total, limit=limit, offset=offset)

    async def get(self, session: AsyncSession, task_id: UUID) -> Task:
        task = await self.repository.get(session, task_id)
        if task is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
        return task

    async def cancel(self, session: AsyncSession, task_id: UUID) -> Task:
        task = await self.get(session, task_id)
        if task.status in {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED}:
            raise HTTPException(status.HTTP_409_CONFLICT, "Task cannot be cancelled")

        task.status = TaskStatus.CANCELLED
        task.finished_at = datetime.now(UTC)
        return await self.repository.save(session, task)


def get_task_service() -> TaskService:
    return TaskService(TaskRepository(), TaskProducer())
