from http import HTTPStatus
import logging
from fastapi import APIRouter, HTTPException

from app.security import get_user, get_password_hash
from app.database import database, user_table
from app.schemas.user import UserCreate, User

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
    hashed_password = get_password_hash(user.password)
    query = user_table.insert().values(email=user.email, password=hashed_password)

    logger.debug(query)

    last_record_id = await database.execute(query)
    new_user = {"email": user.email, "id": last_record_id}
    return User(**new_user)
