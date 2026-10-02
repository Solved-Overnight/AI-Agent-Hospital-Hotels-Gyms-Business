from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "BrightSmile Dental AI API"
    assert "database" in data


def test_chat_validation():
    response = client.post(
        "/api/chat",
        json={
            "message": "",
        },
    )

    assert response.status_code == 422