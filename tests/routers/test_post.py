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
