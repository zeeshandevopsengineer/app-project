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
    assert response.json["status"] == "healthy"

def test_get_tasks(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) >= 2

def test_create_task(client):
    response = client.post("/tasks", json={"title": "Practice CI/CD"})
    assert response.status_code == 201
    assert response.json["title"] == "Practice CI/CD"

def test_create_task_without_title(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 400
    assert response.json["error"] == "title is required"

def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"CI/CD Pipeline Dashboard" in response.data

def test_record_deployment(client):
    response = client.post("/deploy", json={
        "deployment_engineer": "Test Engineer",
        "deployment_name": "Test Feature",
        "commit_message": "test: Test commit",
        "important_notice": "Test notice",
        "message_of_the_day": "Test MOTD"
    })
    assert response.status_code == 200
    assert response.json["status"] == "deployment recorded"
