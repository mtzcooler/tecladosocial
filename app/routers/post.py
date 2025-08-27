from http import HTTPStatus
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Annotated
import logging
import sqlalchemy

from app.database import database, post_table, comment_table, like_table
from app.schemas.post import (
    PostCreate,
    PostRead,
    CommentCreate,
    CommentRead,
    LikeRead,
    PostWithCommentsAndLikes,
)
from app.schemas.user import UserRead
from app.security import get_authenticated_user

router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)

logger = logging.getLogger(__name__)

select_post_and_likes = (
    sqlalchemy.select(post_table, sqlalchemy.func.count(like_table.c.id).label("likes"))
    .select_from(post_table.outerjoin(like_table))
    .group_by(post_table.c.id)
)


async def find_post(post_id: int) -> dict:
    logger.info(f"Finding post with id {post_id}")
    query = post_table.select().where(post_table.c.id == post_id)
    logger.debug(query)
    return await database.fetch_one(query)


@router.post("", name="Create post", status_code=HTTPStatus.CREATED)
async def create_post(
    post: PostCreate, current_user: Annotated[UserRead, Depends(get_authenticated_user)]
) -> PostRead:
    logger.info("Creating post")
    data = {**post.model_dump(), "user_id": current_user.id}
    query = post_table.insert().values(data)
    logger.debug(query)
    last_record_id = await database.execute(query)
    new_post = {**data, "id": last_record_id}
    return PostRead(**new_post)


@router.get("", name="List posts", status_code=HTTPStatus.OK)
async def list_posts() -> List[PostRead]:
    logger.info("Getting all posts")
    query = post_table.select()
    logger.debug(query)
    return await database.fetch_all(query)


@router.post(
    "/{post_id}/comments", name="Create comment", status_code=HTTPStatus.CREATED
)
async def create_comment(
    post_id: int,
    comment: CommentCreate,
    current_user: Annotated[UserRead, Depends(get_authenticated_user)],
) -> CommentRead:
    logger.info("Creating comment")
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Post not found")

    data = comment.model_dump()
    data = {**data, "post_id": post_id, "user_id": current_user.id}
    query = comment_table.insert().values(data)
    logger.debug(query)
    last_record_id = await database.execute(query)
    new_comment = {**data, "id": last_record_id}
    return CommentRead(**new_comment)


@router.get("/{post_id}/comments", name="List comments", status_code=HTTPStatus.OK)
async def list_comments(post_id: int) -> List[CommentRead]:
    logger.info("Getting comments on post")
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    logger.debug(query)
    return await database.fetch_all(query)


@router.get("/{post_id}", name="Get post with comments", status_code=HTTPStatus.OK)
async def read_post_with_comments(post_id: int) -> PostWithCommentsAndLikes:
    logger.info("Getting post and its comments")

    query = select_post_and_likes.where(post_table.c.id == post_id)
    logger.debug(query)
    post_with_likes = await database.fetch_one(query)
    if not post_with_likes:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Post not found")

    posts_with_comments_and_likes = {
        "post": post_with_likes,
        "comments": await list_comments(post_id),
    }
    return PostWithCommentsAndLikes(**posts_with_comments_and_likes)


@router.post("/{post_id}/like", name="Like post", status_code=HTTPStatus.CREATED)
async def like_post(
    post_id: int, current_user: Annotated[UserRead, Depends(get_authenticated_user)]
) -> LikeRead:
    logger.info("Liking post")

    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Post not found")

    data = {"post_id": post_id, "user_id": current_user.id}
    query = like_table.insert().values(data)

    logger.debug(query)

    last_record_id = await database.execute(query)
    data = {**data, "id": last_record_id}
    return LikeRead(**data)
