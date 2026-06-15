from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_register(client):
    response = client.post(
        "/auth/register/",
        json={
            "username": "sujit",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "User sujit created"


def test_register_duplicate(client):
    client.post(
        "/auth/register/",
        json={
            "username": "sujit",
            "password": "password123",
        },
    )
    response = client.post(
        "/auth/register/",
        json={
            "username": "sujit",
            "password": "pass",
        },
    )

    assert response.status_code == 400


def test_login(client):
    client.post(
        "/auth/register/",
        json={
            "username": "sujit",
            "password": "password123",
        },
    )
    response = client.post(
        "/auth/login/",
        data={
            "username": "sujit",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    client.post(
        "/auth/register/",
        json={
            "username": "sujit",
            "password": "password123",
        },
    )
    response = client.post(
        "/auth/login/",
        data={
            "username": "sujit",
            "password": "wrongpass",
        },
    )

    assert response.status_code == 401
