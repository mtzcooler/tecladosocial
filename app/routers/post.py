from http import HTTPStatus
from fastapi import APIRouter, HTTPException
from typing import List

from app.schemas.post import (
    PostCreate,
    PostRead,
    CommentCreate,
    CommentRead,
    PostWithComments,
)

post_table = {}
comment_table = {}

router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


async def find_post(post_id: int) -> dict:
    return post_table.get(post_id, {})


@router.post("", name="Create post", status_code=HTTPStatus.CREATED)
async def create_post(post: PostCreate) -> PostRead:
    data = post.model_dump()
    last_record_id = len(post_table)
    new_post = {**data, "id": last_record_id}
    post_table[last_record_id] = new_post
    return PostRead(**new_post)


@router.get("", name="List posts", status_code=HTTPStatus.OK)
async def list_posts() -> List[PostRead]:
    return list(post_table.values())


@router.post(
    "/{post_id}/comments", name="Create comment", status_code=HTTPStatus.CREATED
)
async def create_comment(post_id: int, comment: CommentCreate) -> CommentRead:
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Post not found")

    data = comment.dict()
    last_record_id = len(comment_table)
    new_comment = {**data, "post_id": post_id, "id": last_record_id}
    comment_table[last_record_id] = new_comment
    return CommentRead(**new_comment)


@router.get("/{post_id}/comments", name="List comments", status_code=HTTPStatus.OK)
async def list_comments(post_id: int) -> List[CommentRead]:
    return [
        comment for comment in comment_table.values() if comment["post_id"] == post_id
    ]


@router.get("/{post_id}", name="Get post with comments", status_code=HTTPStatus.OK)
async def read_post_with_comments(post_id: int) -> PostWithComments:
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Post not found")

    posts_with_comments = {
        "post": post,
        "comments": await list_comments(post_id),
    }
    return PostWithComments(**posts_with_comments)
