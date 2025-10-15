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


async def like_post(
    post_id: int, async_client: AsyncClient, logged_in_token: str
) -> dict:
    response = await async_client.post(
        f"/posts/{post_id}/like",
        json={},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    return response.json()


@pytest.fixture()
async def created_post(async_client: AsyncClient, logged_in_token: str) -> dict:
    return await create_post("Test post", async_client, logged_in_token)


@pytest.fixture()
async def created_post_with_like(
    async_client: AsyncClient, logged_in_token: str
) -> dict:
    post = await create_post("Test post with like", async_client, logged_in_token)
    await like_post(post["id"], async_client, logged_in_token)
    return post


@pytest.fixture()
async def created_comment(
    async_client: AsyncClient, created_post: dict, logged_in_token: str
) -> dict:
    return await create_comment(
        "Test comment", created_post["id"], async_client, logged_in_token
    )


@pytest.fixture()
async def logged_in_token(
    async_client: AsyncClient, confirmed_user_with_password: dict
) -> str:
    response = await async_client.post(
        "/login",
        data={
            "username": confirmed_user_with_password["email"],
            "password": confirmed_user_with_password["password"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return response.json()["access_token"]
