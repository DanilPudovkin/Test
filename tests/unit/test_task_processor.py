import pytest

from app.models.enums import TaskPriority, TaskStatus
from app.models.task import Task
from app.services.task_processor import TaskProcessor


@pytest.mark.asyncio
async def test_task_processor_returns_result() -> None:
    task = Task(
        title="Test task",
        description="Description",
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.IN_PROGRESS,
    )

    result = await TaskProcessor().process(task)

    assert "processed" in result

