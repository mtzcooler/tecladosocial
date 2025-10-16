from http import HTTPStatus
import logging
from typing import Annotated
from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.security import (
    get_user,
    get_password_hash,
    authenticate_user,
    create_access_token,
    create_confirmation_token,
    get_subject_for_token_type,
)
from app.database import database, user_table
from app.schemas.user import UserCreate, UserRead
from app.tasks import send_user_registration_email


logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["Users"],
)


@router.post("/register", status_code=HTTPStatus.CREATED)
async def register(user: UserCreate, request: Request) -> UserRead:
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

    await send_user_registration_email(
        user.email,
        request.url_for("confirm_email", token=create_confirmation_token(user.email)),
    )
    return UserRead(**new_user)


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> dict:
    user = await authenticate_user(form_data.username, form_data.password)
    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirm/{token}")
async def confirm_email(token: str) -> dict:
    email = get_subject_for_token_type(token, "confirmation")
    query = (
        user_table.update().where(user_table.c.email == email).values(confirmed=True)
    )

    logger.debug(query)

    await database.execute(query)
    return {"detail": "User confirmed."}
