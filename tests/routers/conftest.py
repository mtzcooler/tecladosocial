import pytest
from httpx import AsyncClient


async def create_post(
    body: str, async_client: AsyncClient, logged_in_token: str
) -> dict:
    response = await async_client.post(
        "/posts",
        json={"body": body},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    return response.json()


async def create_comment(
    body: str, post_id: int, async_client: AsyncClient, logged_in_token: str
) -> dict:
    response = await async_client.post(
        f"/posts/{post_id}/comments",
        json={"body": body},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    return response.json()


async def create_user(email: str, password: str, async_client: AsyncClient) -> dict:
    response = await async_client.post(
        "/register", json={"email": email, "password": password}
    )
    return response.json()


@pytest.fixture()
async def created_post(async_client: AsyncClient, logged_in_token: str) -> dict:
    return await create_post("Test post", async_client, logged_in_token)


@pytest.fixture()
async def created_comment(
    async_client: AsyncClient, created_post: dict, logged_in_token: str
) -> dict:
    return await create_comment(
        "Test comment", created_post["id"], async_client, logged_in_token
    )


@pytest.fixture()
async def registered_user(async_client: AsyncClient) -> dict:
    user_details = await create_user("test@example.com", "1234", async_client)
    return user_details


@pytest.fixture()
async def registered_user_with_password(async_client: AsyncClient) -> dict:
    password = "1234"
    user_details = await create_user("test@example.com", password, async_client)
    return {**user_details, "password": password}


@pytest.fixture()
async def logged_in_token(
    async_client: AsyncClient, registered_user_with_password: dict
) -> str:
    response = await async_client.post("/login", json=registered_user_with_password)
    return response.json()["access_token"]
