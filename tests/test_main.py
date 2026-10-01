from fastapi.testclient import TestClient

from app.main import app

# тестовый клиент для приложения
client = TestClient(app)

# первый тест для нашего простого запроса
def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Task Manager API is running"
    }
