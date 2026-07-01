import json
import os
import time
from urllib import request

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_E2E") != "1",
    reason="requires running Docker Compose services",
)


def _request_json(url: str, method: str = "GET", payload: dict | None = None) -> dict:
    body = None
    headers = {}
    if payload is not None:
        body = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"

    req = request.Request(url, data=body, headers=headers, method=method)
    with request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode())


def test_task_is_processed_by_worker() -> None:
    ready = _request_json("http://localhost:8000/health/ready")
    assert ready["status"] == "ok"

    task = _request_json(
        "http://localhost:8000/api/v1/tasks",
        method="POST",
        payload={
            "title": "E2E task",
            "description": "Created by the e2e smoke test",
            "priority": "HIGH",
        },
    )

    for _ in range(10):
        current = _request_json(f"http://localhost:8000/api/v1/tasks/{task['id']}")
        if current["status"] in {"COMPLETED", "FAILED"}:
            break
        time.sleep(1)
    else:
        pytest.fail("task did not reach a terminal state")

    assert current["status"] == "COMPLETED"
    assert current["result"] is not None
