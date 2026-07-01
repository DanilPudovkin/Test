# Architecture Notes

This file is a short map of the project. The README contains the main run instructions.

## Components

- `app/api` - FastAPI routers and HTTP contracts.
- `app/schemas` - Pydantic request and response schemas.
- `app/services` - business logic and task lifecycle rules.
- `app/repositories` - database access through SQLAlchemy.
- `app/models` - SQLAlchemy models and domain enums.
- `app/messaging` - RabbitMQ publishing.
- `app/worker.py` - background consumer that processes queued tasks.
- `alembic` - database migrations.

## Task Flow

1. Client sends `POST /api/v1/tasks`.
2. API validates payload with `TaskCreate`.
3. `TaskService` creates a task with `PENDING` status.
4. `TaskProducer` publishes task id to RabbitMQ with priority.
5. Worker consumes the message and changes status to `IN_PROGRESS`.
6. `TaskProcessor` performs the background work.
7. Worker marks task as `COMPLETED` or `FAILED`.

If RabbitMQ is unavailable during creation, the task is marked as `FAILED` and the API returns `503`.

## Status Model

- `NEW` - task object was created but not yet queued.
- `PENDING` - task is queued and waiting for worker.
- `IN_PROGRESS` - worker is processing the task.
- `COMPLETED` - task finished successfully.
- `FAILED` - task finished with an error.
- `CANCELLED` - task was cancelled by API request.

## Scaling

The API and worker are separate processes. To increase throughput, run more worker replicas or increase `WORKER_CONCURRENCY`. RabbitMQ priority queue keeps high-priority tasks ahead of lower-priority tasks.
