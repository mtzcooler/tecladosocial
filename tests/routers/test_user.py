from http import HTTPStatus

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    email = "test@example.net"
    password = "password"
    response = await async_client.post(
        "/register", json={"email": email, "password": password}
    )
    assert response.status_code == HTTPStatus.CREATED
    assert {"id": 1, "email": email}.items() <= response.json().items()


@pytest.mark.anyio
async def test_register_user_already_exists(
    async_client: AsyncClient, registered_user: dict
):
    response = await async_client.post(
        "/register",
        json={
            "email": registered_user["email"],
            "password": "password",
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert "already exists" in response.json()["detail"]


@pytest.mark.anyio
async def test_login_user_not_exists(async_client: AsyncClient):
    response = await async_client.post(
        "/login", json={"email": "test@example.net", "password": "1234"}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Inexistent user"}


@pytest.mark.anyio
async def test_login_user(
    async_client: AsyncClient, registered_user_with_password: dict
):
    response = await async_client.post(
        "/login",
        json={
            "email": registered_user_with_password["email"],
            "password": registered_user_with_password["password"],
        },
    )
    assert response.status_code == HTTPStatus.OK


@pytest.mark.anyio
async def test_login_user_wrong_password(
    async_client: AsyncClient, registered_user: dict
):
    response = await async_client.post(
        "/login",
        json={
            "email": registered_user["email"],
            "password": "wrong password",
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Invalid credentials"}
