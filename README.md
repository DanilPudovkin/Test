# Async Task Service

Сервис для асинхронной обработки задач. В проекте есть API на FastAPI,
PostgreSQL для хранения задач, RabbitMQ как очередь и отдельный worker,
который забирает задачи из очереди и обрабатывает их в фоне.

Запуск и проверки сделаны через Docker Compose и `make`.

## Стек

- Python 3.12
- FastAPI
- SQLAlchemy async ORM
- PostgreSQL 14
- RabbitMQ
- Alembic
- pytest
- Docker Compose
- Make

## Что реализовано

- Создание задач через REST API.
- Сохранение задач в PostgreSQL.
- Отправка задач в RabbitMQ.
- Фоновая обработка задач отдельным worker-процессом.
- Параллельная обработка через настройку `WORKER_CONCURRENCY`.
- Приоритеты задач: `LOW`, `MEDIUM`, `HIGH`.
- Статусы задач: `NEW`, `PENDING`, `IN_PROGRESS`, `COMPLETED`, `FAILED`, `CANCELLED`.
- Фильтрация и пагинация списка задач.
- Unit/API/e2e тесты.

## Запуск

Нужны Docker, Docker Compose и Make.

Перед запуском нужно создать `.env` из примера:

```bash
cp .env.example .env
```

Запуск проекта:

```bash
make up
```

Swagger:

```text
http://localhost:8000/docs
```

RabbitMQ UI:

```text
http://localhost:15672
guest / guest
```

Остановка контейнеров:

```bash
make down
```

## API

```text
POST   /api/v1/tasks
GET    /api/v1/tasks
GET    /api/v1/tasks/{task_id}
DELETE /api/v1/tasks/{task_id}
GET    /api/v1/tasks/{task_id}/status
```

## Тесты

Тесты запускаются внутри поднятого окружения:

```bash
make test
```

E2E-тест:

```bash
make test-e2e
```

Линтер:

```bash
make lint
```

## Как работает обработка задачи

1. Клиент отправляет `POST /api/v1/tasks`.
2. API валидирует данные и создает задачу со статусом `PENDING`.
3. ID задачи публикуется в RabbitMQ.
4. Worker забирает ID задачи из очереди.
5. Worker переводит задачу в `IN_PROGRESS`.
6. После обработки задача становится `COMPLETED` или `FAILED`.

Если RabbitMQ недоступен во время создания задачи, задача помечается как `FAILED`,
а API возвращает `503`. Так в базе не остаются задачи в `PENDING`, которые на самом
деле не попали в очередь.

## Упрощения

- В `TaskProcessor` сейчас демонстрационная обработка: небольшая задержка и возврат строки с результатом.
- Авторизации нет, потому что ее не было в требованиях.
- Dead-letter queue не добавлял. Ошибка обработки фиксируется в задаче через статус `FAILED` и поле `error`.
