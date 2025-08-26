from http import HTTPStatus
import logging
from fastapi import APIRouter, HTTPException
from app.schemas.user import UserCreate, User
from app.security import get_user
from app.database import database, user_table

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("/register", status_code=HTTPStatus.CREATED)
async def register(user: UserCreate) -> User:
    if await get_user(user.email):
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="A user with that email already exists.",
        )
    query = user_table.insert().values(email=user.email, password=user.password)

    logger.debug(query)

    last_record_id = await database.execute(query)
    new_user = {"email": user.email, "id": last_record_id}
    return User(**new_user)
