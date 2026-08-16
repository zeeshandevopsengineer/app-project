import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200

def test_get_tasks(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_create_task(client):
    response = client.post("/tasks", json={"title": "Test Task"})
    assert response.status_code == 201

def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"CI/CD" in response.data

def test_record_deployment(client):
    response = client.post("/deploy", json={"deployment_name": "Test"})
    assert response.status_code == 200
