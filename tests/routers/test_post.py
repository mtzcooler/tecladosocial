import pytest
from httpx import AsyncClient
from http import HTTPStatus


@pytest.mark.anyio
async def test_create_post(
    async_client: AsyncClient, logged_in_token: str, registered_user_with_password
):
    body = "Test Post"
    response = await async_client.post(
        "/posts",
        json={"body": body},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert {
        "id": 1,
        "body": body,
        "user_id": registered_user_with_password["id"],
    }.items() <= response.json().items()


@pytest.mark.anyio
async def test_create_post_missing_data(
    async_client: AsyncClient, logged_in_token: str
):
    response = await async_client.post(
        "/posts",
        json={},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_list_all_posts(async_client: AsyncClient, created_post: dict):
    response = await async_client.get("/posts")

    assert response.status_code == HTTPStatus.OK
    assert created_post.items() <= response.json()[0].items()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "sorting, expected_order",
    [
        ("-id", [2, 1]),
        ("+id", [1, 2]),
    ],
)
async def test_list_all_posts_sorting(
    async_client: AsyncClient,
    logged_in_token: str,
    created_post: dict,
    created_post_with_like: dict,
    sorting: str,
    expected_order: list[int],
):
    response = await async_client.get("/posts", params={"sorting": sorting})
    assert response.status_code == HTTPStatus.OK

    data = response.json()
    post_ids = [post["id"] for post in data]
    assert post_ids == expected_order


@pytest.mark.anyio
async def test_get_all_posts_sorting_likes(
    async_client: AsyncClient,
    logged_in_token: str,
    created_post: dict,
    created_post_with_like: dict,
):
    response = await async_client.get("/posts", params={"sorting": "-likes"})
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert [post["id"] for post in data] == [2, 1]


@pytest.mark.anyio
async def test_create_comment(
    async_client: AsyncClient,
    created_post: dict,
    logged_in_token: str,
    registered_user_with_password,
):
    body = "Test comment"
    post_id = created_post["id"]
    response = await async_client.post(
        f"/posts/{post_id}/comments",
        json={"body": body},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert {
        "id": 1,
        "post_id": post_id,
        "user_id": registered_user_with_password["id"],
        "body": body,
    }.items() <= response.json().items()


@pytest.mark.anyio
async def test_get_comments_on_post(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get(f"/posts/{created_post['id']}/comments")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [created_comment]


@pytest.mark.anyio
async def test_get_comments_on_post_without_comments(
    async_client: AsyncClient, created_post: dict
):
    response = await async_client.get(f"/posts/{created_post['id']}/comments")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


@pytest.mark.anyio
async def test_post_with_comments(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get(f"/posts/{created_post['id']}")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "post": {**created_post, "likes": 0},
        "comments": [created_comment],
    }


@pytest.mark.anyio
async def test_get_missing_post_with_comments(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get("/posts/2")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.anyio
async def test_like_post(
    async_client: AsyncClient, created_post: dict, logged_in_token: str
):
    response = await async_client.post(
        f"/posts/{created_post['id']}/like",
        json={},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    assert response.status_code == HTTPStatus.CREATED
