import asyncio
import logging
from datetime import UTC, datetime
from uuid import UUID

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.enums import TaskStatus
from app.repositories.task_repository import TaskRepository
from app.services.task_processor import TaskProcessor

logger = logging.getLogger(__name__)


async def handle_message(message: AbstractIncomingMessage) -> None:
    async with message.process(requeue=False):
        task_id = UUID(message.body.decode())
        repository = TaskRepository()
        processor = TaskProcessor()

        async with SessionLocal() as session:
            task = await repository.get(session, task_id)
            if task is None or task.status == TaskStatus.CANCELLED:
                return

            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now(UTC)
            await repository.save(session, task)

            try:
                result = await processor.process(task)
                final_status = TaskStatus.COMPLETED
                final_result = result
                final_error = None
            except Exception as exc:
                final_status = TaskStatus.FAILED
                final_result = None
                final_error = str(exc)

            await session.refresh(task)
            if task.status == TaskStatus.CANCELLED:
                return

            task.result = final_result
            task.error = final_error
            task.status = final_status
            task.finished_at = datetime.now(UTC)
            await repository.save(session, task)


async def main() -> None:
    connection = None
    while connection is None:
        try:
            connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        except Exception as exc:
            logger.warning("RabbitMQ is not ready yet: %s", exc)
            await asyncio.sleep(2)

    channel = await connection.channel()
    await channel.set_qos(prefetch_count=settings.worker_concurrency)
    queue = await channel.declare_queue(
        settings.task_queue_name,
        durable=True,
        arguments={"x-max-priority": 10},
    )
    await queue.consume(handle_message)

    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
