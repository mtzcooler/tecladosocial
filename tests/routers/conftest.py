import pytest
from httpx import AsyncClient


async def create_post(body: str, async_client: AsyncClient) -> dict:
    response = await async_client.post("/posts", json={"body": body})
    return response.json()


@pytest.fixture()
async def created_post(async_client: AsyncClient) -> dict:
    return await create_post("Test post", async_client)
