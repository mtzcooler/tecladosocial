from http import HTTPStatus

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    email = "test@example.net"
    password = "password"
    response = await async_client.post(
        "/users/register", json={"email": email, "password": password}
    )
    assert response.status_code == HTTPStatus.CREATED
    assert {"id": 1, "email": email}.items() <= response.json().items()


@pytest.mark.anyio
async def test_register_user_already_exists(
    async_client: AsyncClient, registered_user: dict
):
    response = await async_client.post(
        "/users/register",
        json={
            "email": registered_user["email"],
            "password": "password",
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert "already exists" in response.json()["detail"]
