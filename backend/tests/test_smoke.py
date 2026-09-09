from fastapi.testclient import TestClient

from app.main import app
from app.API.routes.archon import service


client = TestClient(app)


def test_app_starts():
    response = client.get("/docs")

    assert response.status_code == 200


def test_start_archon(monkeypatch):
    async def mock_run(thread_id: str, user_goal: str):
        return None

    monkeypatch.setattr(service, "run", mock_run)

    response = client.post(
        "/api/v1/archon",
        json={
            "user_goal": "Build a document question answering system"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "thread_id" in data
    assert data["status"] == "running"
    assert data["user_goal"] == "Build a document question answering system"


def test_invalid_start_archon_request():
    response = client.post(
        "/api/v1/archon",
        json={},
    )

    assert response.status_code == 422