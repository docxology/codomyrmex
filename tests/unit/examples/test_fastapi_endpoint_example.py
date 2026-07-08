import pytest
from fastapi.testclient import TestClient

import codomyrmex.examples.fastapi_endpoint_example as example_module
from codomyrmex.examples.fastapi_endpoint_example import create_app


@pytest.fixture
def client():
    # Clear fake db before each test
    example_module.fake_users_db.clear()
    example_module.current_id = 0
    app = create_app()
    return TestClient(app)


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_user(client):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "created_at" in data


def test_create_duplicate_user(client):
    user_data = {"username": "testuser", "email": "test@example.com"}
    # First creation
    client.post("/users/", json=user_data)
    # Duplicate creation
    response = client.post("/users/", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"


def test_read_users(client):
    # Create two users
    client.post("/users/", json={"username": "user1", "email": "u1@example.com"})
    client.post("/users/", json={"username": "user2", "email": "u2@example.com"})

    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["username"] == "user1"


def test_read_user_by_id(client):
    # Create user
    create_resp = client.post(
        "/users/", json={"username": "user1", "email": "u1@example.com"}
    )
    user_id = create_resp.json()["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["username"] == "user1"


def test_read_user_not_found(client):
    response = client.get("/users/999")
    assert response.status_code == 404
