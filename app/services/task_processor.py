import asyncio

from app.models.task import Task


class TaskProcessor:
    async def process(self, task: Task) -> str:
        await asyncio.sleep(1)
        return f"Task {task.id} processed"

