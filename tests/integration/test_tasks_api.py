from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.db.session import get_session
from app.main import app
from app.models.enums import TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskListRead, TaskRead
from app.services.task_service import get_task_service


class FakeTaskService:
    def __init__(self) -> None:
        self.task = TaskRead(
            id=UUID("11111111-1111-1111-1111-111111111111"),
            title="Initial task",
            description="Initial description",
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.PENDING,
            created_at=datetime.now(UTC),
            started_at=None,
            finished_at=None,
            result=None,
            error=None,
        )

    async def create(self, session, payload: TaskCreate) -> TaskRead:
        return TaskRead(
            id=uuid4(),
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
            status=TaskStatus.PENDING,
            created_at=datetime.now(UTC),
            started_at=None,
            finished_at=None,
            result=None,
            error=None,
        )

    async def list(
        self,
        session,
        status_filter: TaskStatus | None,
        priority: TaskPriority | None,
        limit: int,
        offset: int,
    ) -> TaskListRead:
        return TaskListRead(items=[self.task], total=1, limit=limit, offset=offset)

    async def get(self, session, task_id: UUID) -> TaskRead:
        return self.task.model_copy(update={"id": task_id})

    async def cancel(self, session, task_id: UUID) -> TaskRead:
        return self.task.model_copy(update={"id": task_id, "status": TaskStatus.CANCELLED})


def override_session():
    return object()


def test_create_task_endpoint() -> None:
    app.dependency_overrides[get_task_service] = FakeTaskService
    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)

    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Generate report",
            "description": "Prepare monthly report",
            "priority": "HIGH",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Generate report"
    assert body["priority"] == "HIGH"
    assert body["status"] == "PENDING"


def test_list_tasks_endpoint_returns_page() -> None:
    app.dependency_overrides[get_task_service] = FakeTaskService
    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)

    response = client.get("/api/v1/tasks?limit=10&offset=0")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["limit"] == 10
    assert body["offset"] == 0
    assert len(body["items"]) == 1


def test_get_task_status_endpoint() -> None:
    app.dependency_overrides[get_task_service] = FakeTaskService
    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)

    task_id = "22222222-2222-2222-2222-222222222222"
    response = client.get(f"/api/v1/tasks/{task_id}/status")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"id": task_id, "status": "PENDING"}
