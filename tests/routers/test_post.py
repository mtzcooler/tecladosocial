import pytest
from httpx import AsyncClient
from http import HTTPStatus


@pytest.mark.anyio
async def test_create_post(async_client: AsyncClient):
    body = "Test Post"
    response = await async_client.post(
        "/posts",
        json={"body": body},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert {"id": 0, "body": "Test Post"}.items() <= response.json().items()


@pytest.mark.anyio
async def test_create_post_missing_data(async_client: AsyncClient):
    response = await async_client.post(
        "/posts",
        json={},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_list_all_posts(async_client: AsyncClient, created_post: dict):
    response = await async_client.get("/posts")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [created_post]
