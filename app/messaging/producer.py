from uuid import UUID

import aio_pika

from app.core.config import settings
from app.models.enums import TaskPriority

PRIORITY_MAP = {
    TaskPriority.LOW: 1,
    TaskPriority.MEDIUM: 5,
    TaskPriority.HIGH: 9,
}


class TaskProducer:
    async def publish_task(self, task_id: UUID, priority: TaskPriority) -> None:
        connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(
                settings.task_queue_name,
                durable=True,
                arguments={"x-max-priority": 10},
            )
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=str(task_id).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    priority=PRIORITY_MAP[priority],
                ),
                routing_key=queue.name,
            )

