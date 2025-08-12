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
from app.database import database, post_table, comment_table

router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


async def find_post(post_id: int) -> dict:
    query = post_table.select().where(post_table.c.id == post_id)
    return await database.fetch_one(query)


@router.post("", name="Create post", status_code=HTTPStatus.CREATED)
async def create_post(post: PostCreate) -> PostRead:
    data = post.model_dump()
    query = post_table.insert().values(data)
    last_record_id = await database.execute(query)
    new_post = {**data, "id": last_record_id}
    return PostRead(**new_post)


@router.get("", name="List posts", status_code=HTTPStatus.OK)
async def list_posts() -> List[PostRead]:
    query = post_table.select()
    return await database.fetch_all(query)


@router.post(
    "/{post_id}/comments", name="Create comment", status_code=HTTPStatus.CREATED
)
async def create_comment(post_id: int, comment: CommentCreate) -> CommentRead:
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Post not found")

    data = comment.model_dump()
    data = {**data, "post_id": post_id}
    query = comment_table.insert().values(data)
    last_record_id = await database.execute(query)
    new_comment = {**data, "id": last_record_id}
    return CommentRead(**new_comment)


@router.get("/{post_id}/comments", name="List comments", status_code=HTTPStatus.OK)
async def list_comments(post_id: int) -> List[CommentRead]:
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    return await database.fetch_all(query)


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
