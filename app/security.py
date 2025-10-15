import logging
from http import HTTPStatus
from typing import Annotated, Literal
from fastapi import HTTPException, Depends
import bcrypt
import datetime
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, ExpiredSignatureError, JWTError

from app.config import config
from app.database import database, user_table


logger = logging.getLogger(__name__)

SECRET_KEY = config.APP_SECRET
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def unauthorized_exception(message: str) -> HTTPException:
    return HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)


def access_token_expire_minutes() -> int:
    return 30


def confirm_token_expire_minutes() -> int:
    return 1440


def create_access_token(email: str):
    logger.debug("Creating access token", extra={"email": email})
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=access_token_expire_minutes()
    )
    jwt_data = {"sub": email, "exp": expire, "type": "access"}
    encoded_jwt = jwt.encode(jwt_data, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_confirmation_token(email: str):
    logger.debug("Creating confirmation token", extra={"email": email})
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=confirm_token_expire_minutes()
    )
    jwt_data = {"sub": email, "exp": expire, "type": "confirmation"}
    encoded_jwt = jwt.encode(jwt_data, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_subject_for_token_type(
    token: str, type: Literal["access", "confirmation"]
) -> str:
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError as e:
        raise unauthorized_exception("Token has expired") from e
    except JWTError as e:
        raise unauthorized_exception("Invalid token") from e

    email = payload.get("sub")
    if email is None:
        raise unauthorized_exception("Token is missing 'sub' field")

    token_type = payload.get("type")
    if token_type != type:
        raise unauthorized_exception(f"Token has incorrect type, expected '{type}'")

    return email


async def get_user(email: str):
    logger.debug("Fetching user from the database", extra={"email": email})
    query = user_table.select().where(user_table.c.email == email)
    result = await database.fetch_one(query)
    if result:
        return result
    return None


async def authenticate_user(email: str, password: str):
    logger.debug("Authenticating user", extra={"email": email})
    user = await get_user(email)
    if not user:
        raise unauthorized_exception("Inexistent user")
    if not verify_password(password, user.password):
        raise unauthorized_exception("Invalid credentials")
    if not user.confirmed:
        raise unauthorized_exception("User has not confirmed email")
    return user


async def get_authenticated_user(token: Annotated[str, Depends(oauth2_scheme)]):
    email = get_subject_for_token_type(token, type="access")
    user = await get_user(email=email)
    if user is None:
        raise unauthorized_exception("Could not find user for this token")
    return user
