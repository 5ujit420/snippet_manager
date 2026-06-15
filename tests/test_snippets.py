from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def get_token(client):
    client.post(
        "/auth/register/",
        json={
            "username": "sujit",
            "password": "pass",
        },
    )
    response = client.post(
        "/auth/login/",
        data={
            "username": "sujit",
            "password": "pass",
        },
    )
    return response.json()["access_token"]


def test_create_snippet(client):
    token = get_token(client)
    response = client.post(
        "/snippets/",
        json={
            "title": "Hello",
            "code": "print('hi')",
            "language": "pythono",
            "tags": "python",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Hello"


def test_list_snippet(client):
    token = get_token(client)
    client.post(
        "/snippets/",
        json={
            "title": "Hello",
            "code": "print('hi')",
            "language": "pythono",
            "tags": "python",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.get("/snippets/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_unauthorized(client):
    response = client.get("/snippets/")
    assert response.status_code == 401
