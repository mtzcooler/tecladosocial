from http import HTTPStatus
import logging
from typing import Annotated
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.security import (
    get_user,
    get_password_hash,
    authenticate_user,
    create_access_token,
)
from app.database import database, user_table
from app.schemas.user import UserCreate, UserRead


logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["Users"],
)


@router.post("/register", status_code=HTTPStatus.CREATED)
async def register(user: UserCreate) -> UserRead:
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
    return UserRead(**new_user)


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> dict:
    user = await authenticate_user(form_data.username, form_data.password)
    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}
