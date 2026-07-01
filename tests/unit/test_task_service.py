from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models.enums import TaskPriority, TaskStatus
from app.models.task import Task
from app.schemas.task import TaskCreate
from app.services.task_service import TaskService


class FakeTaskRepository:
    def __init__(self, task: Task | None = None) -> None:
        self.task = task
        self.saved_task: Task | None = None

    async def create(self, session, task: Task) -> Task:
        return task

    async def get(self, session, task_id) -> Task | None:
        return self.task

    async def save(self, session, task: Task) -> Task:
        self.saved_task = task
        return task


class FailingTaskProducer:
    async def publish_task(self, task_id, priority) -> None:
        raise ConnectionError("RabbitMQ is down")


class NoopTaskProducer:
    async def publish_task(self, task_id, priority) -> None:
        return None


@pytest.mark.asyncio
async def test_create_marks_task_failed_when_queue_is_unavailable() -> None:
    repository = FakeTaskRepository()
    service = TaskService(repository, FailingTaskProducer())

    with pytest.raises(HTTPException) as exc_info:
        await service.create(
            session=object(),
            payload=TaskCreate(
                title="Generate report",
                description="Prepare monthly report",
            ),
        )

    assert exc_info.value.status_code == 503
    assert repository.saved_task is not None
    assert repository.saved_task.status == "FAILED"
    assert repository.saved_task.error == "Failed to enqueue task"


@pytest.mark.asyncio
async def test_cancel_marks_pending_task_cancelled() -> None:
    task = Task(
        id=uuid4(),
        title="Generate report",
        description="Prepare monthly report",
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.PENDING,
    )
    repository = FakeTaskRepository(task)
    service = TaskService(repository, NoopTaskProducer())

    result = await service.cancel(session=object(), task_id=task.id)

    assert result.status == TaskStatus.CANCELLED
    assert result.finished_at is not None


@pytest.mark.asyncio
async def test_cancel_completed_task_raises_conflict() -> None:
    task = Task(
        id=uuid4(),
        title="Generate report",
        description="Prepare monthly report",
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.COMPLETED,
    )
    service = TaskService(FakeTaskRepository(task), NoopTaskProducer())

    with pytest.raises(HTTPException) as exc_info:
        await service.cancel(session=object(), task_id=task.id)

    assert exc_info.value.status_code == 409
