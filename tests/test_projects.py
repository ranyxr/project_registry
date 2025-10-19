from datetime import date, timedelta

from fastapi.testclient import TestClient


def register_user(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "alice@example.com",
            "full_name": "Alice Example",
            "password": "S3curePass!",
        },
    )
    assert response.status_code == 201, response.text


def obtain_token(client: TestClient) -> str:
    response = client.post(
        "/auth/token",
        data={"username": "alice@example.com", "password": "S3curePass!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def test_project_crud_flow(client: TestClient) -> None:
    register_user(client)
    token = obtain_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/projects/",
        json={
            "name": "Data Warehouse",
            "description": "Core analytics platform",
            "expiration_date": (date.today() + timedelta(days=30)).isoformat(),
        },
        headers=headers,
    )
    assert create_response.status_code == 201, create_response.text
    project_id = create_response.json()["id"]

    list_response = client.get("/projects/", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    update_response = client.patch(
        f"/projects/{project_id}",
        json={"description": "Updated description"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["description"] == "Updated description"

    delete_response = client.delete(f"/projects/{project_id}", headers=headers)
    assert delete_response.status_code == 204

    empty_response = client.get("/projects/", headers=headers)
    assert empty_response.status_code == 200
    assert empty_response.json() == []
