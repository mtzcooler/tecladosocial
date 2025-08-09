from http import HTTPStatus
from fastapi import APIRouter
from typing import List

from app.schemas.post import PostCreate, PostRead

post_table = {}

router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


@router.post("", name="Create post", status_code=HTTPStatus.CREATED)
async def create(post: PostCreate) -> PostRead:
    data = post.dict()
    last_record_id = len(post_table)
    new_post = {**data, "id": last_record_id}
    post_table[last_record_id] = new_post
    return PostRead(**new_post)


@router.get("", name="List posts", status_code=HTTPStatus.OK)
async def index() -> List[PostRead]:
    return list(post_table.values())
