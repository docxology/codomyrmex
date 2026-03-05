import pytest
from fastapi.testclient import TestClient
from .fastapi_endpoint import app

client = TestClient(app)


def test_create_item():
    response = client.post(
        "/items/",
        json={"name": "Test Item", "price": 9.99},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["price"] == 9.99
    assert "description" in data


def test_read_items():
    # Ensure at least one item exists
    client.post("/items/", json={"name": "Item 2", "price": 5.0})

    response = client.get("/items/")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_item_not_found():
    response = client.get("/items/999")
    assert response.status_code == 404
