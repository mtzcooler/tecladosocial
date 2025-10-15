from http import HTTPStatus

import pytest
from httpx import AsyncClient
from app.security import create_confirmation_token


async def register_user(async_client: AsyncClient, email: str, password: str):
    return await async_client.post(
        "/register", json={"email": email, "password": password}
    )


@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    email = "test@example.net"
    password = "password"
    response = await register_user(async_client, email, password)
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
async def test_confirm_email(async_client: AsyncClient, mocker):
    email = "test@example.com"
    token = create_confirmation_token(email)
    response = await async_client.get(f"/confirm/{token}")
    assert response.status_code == HTTPStatus.OK, response.json()
    assert response.json()["detail"] == "User confirmed."


@pytest.mark.anyio
async def test_confirm_user_invalid_token(async_client: AsyncClient):
    response = await async_client.get("/confirm/invalid_token")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_confirm_user_expired_token(async_client: AsyncClient, mocker):
    mocker.patch("app.security.confirm_token_expire_minutes", return_value=-1)
    email = "test@example.com"
    token = create_confirmation_token(email)
    response = await async_client.get(f"/confirm/{token}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Token has expired"}


@pytest.mark.anyio
async def test_login_user_not_exists(async_client: AsyncClient):
    response = await async_client.post(
        "/login",
        data={"username": "test@example.com", "password": "1234"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Inexistent user"}


@pytest.mark.anyio
async def test_login_user(
    async_client: AsyncClient, registered_user_with_password: dict
):
    response = await async_client.post(
        "/login",
        data={
            "username": registered_user_with_password["email"],
            "password": registered_user_with_password["password"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == HTTPStatus.OK


@pytest.mark.anyio
async def test_login_user_wrong_password(
    async_client: AsyncClient, registered_user: dict
):
    response = await async_client.post(
        "/login",
        data={
            "username": registered_user["email"],
            "password": "wrong password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Invalid credentials"}
