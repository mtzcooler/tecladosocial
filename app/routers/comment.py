from http import HTTPStatus
from fastapi import APIRouter, HTTPException
from typing import List

from app.schemas.post import CommentCreate, CommentRead, PostWithComments
from app.routers.post import post_table

comment_table = {}

router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


async def find_post(post_id: int) -> dict:
    return post_table.get(post_id, {})


@router.post(
    "/{post_id}/comments", name="Create comment", status_code=HTTPStatus.CREATED
)
async def create(post_id: int, comment: CommentCreate) -> CommentRead:
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Post not found")

    data = comment.dict()
    last_record_id = len(comment_table)
    new_comment = {**data, "post_id": post_id, "id": last_record_id}
    comment_table[last_record_id] = new_comment
    return CommentRead(**new_comment)


@router.get("/{post_id}/comments", name="List comments", status_code=HTTPStatus.OK)
async def index(post_id: int) -> List[CommentRead]:
    return [
        comment for comment in comment_table.values() if comment["post_id"] == post_id
    ]


@router.get("/{post_id}", name="Get post with comments", status_code=HTTPStatus.OK)
async def read(post_id: int) -> PostWithComments:
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Post not found")

    posts_with_comments = {
        "post": post,
        "comments": await index(post_id),
    }
    return PostWithComments(**posts_with_comments)
