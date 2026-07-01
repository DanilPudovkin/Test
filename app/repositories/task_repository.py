from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import TaskPriority, TaskStatus
from app.models.task import Task


class TaskRepository:
    async def create(self, session: AsyncSession, task: Task) -> Task:
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task

    async def get(self, session: AsyncSession, task_id: UUID) -> Task | None:
        return await session.get(Task, task_id)

    def _with_filters(
        self,
        query: Select,
        status: TaskStatus | None,
        priority: TaskPriority | None,
    ) -> Select:
        if status is not None:
            query = query.where(Task.status == status)
        if priority is not None:
            query = query.where(Task.priority == priority)
        return query

    async def list(
        self,
        session: AsyncSession,
        status: TaskStatus | None,
        priority: TaskPriority | None,
        limit: int,
        offset: int,
    ) -> list[Task]:
        query: Select[tuple[Task]] = select(Task).order_by(Task.created_at.desc())
        query = self._with_filters(query, status, priority)

        result = await session.execute(query.limit(limit).offset(offset))
        return list(result.scalars().all())

    async def count(
        self,
        session: AsyncSession,
        status: TaskStatus | None,
        priority: TaskPriority | None,
    ) -> int:
        query = self._with_filters(select(func.count()).select_from(Task), status, priority)
        result = await session.execute(query)
        return int(result.scalar_one())

    async def save(self, session: AsyncSession, task: Task) -> Task:
        await session.commit()
        await session.refresh(task)
        return task
