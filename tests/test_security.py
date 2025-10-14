from jose import jwt
from app import security
import pytest


def test_password_hashes():
    password = "password"
    assert security.verify_password(password, security.get_password_hash(password))


def test_access_token_expire_minutes():
    assert security.access_token_expire_minutes() == 30


def test_confirm_token_expire_minutes():
    assert security.confirm_token_expire_minutes() == 1440


def test_create_access_token():
    token = security.create_access_token("123")
    assert {"sub": "123", "type": "access"}.items() <= jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    ).items()


def test_create_confirmation_token():
    token = security.create_confirmation_token("123")
    assert {"sub": "123", "type": "confirmation"}.items() <= jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    ).items()


def test_get_subject_for_valid_token_type_confirmation():
    email = "test@example.com"
    token = security.create_confirmation_token(email)
    assert email == security.get_subject_for_token_type(token, type="confirmation")


def test_get_subject_for_valid_token_type_access():
    email = "test@example.com"
    token = security.create_access_token(email)
    assert email == security.get_subject_for_token_type(token, type="access")


def test_get_subject_for_wrong_token_type():
    email = "test@example.com"
    token = security.create_confirmation_token(email)
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token has incorrect type, expected 'access'"


def test_get_subject_for_expired_token(mocker):
    mocker.patch("app.security.access_token_expire_minutes", return_value=-1)
    email = ""
    token = security.create_access_token(email)
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, type="access")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token has expired"


def test_get_subject_for_invalid_token(mocker):
    token = "invalid token"
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, type="access")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"


def test_get_subject_for_token_with_missing_sub():
    email = "test@example.com"
    token = security.create_access_token(email)
    payload = jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    )
    del payload["sub"]
    modified_token = jwt.encode(
        payload, key=security.SECRET_KEY, algorithm=security.ALGORITHM
    )

    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(modified_token, type="access")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token is missing 'sub' field"


@pytest.mark.anyio
async def test_get_user(registered_user: dict):
    user = await security.get_user(registered_user["email"])

    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_authenticate_user_not_found():
    with pytest.raises(security.HTTPException):
        await security.authenticate_user("test@example.net", "1234")


@pytest.mark.anyio
async def test_authenticate_user_wrong_password(registered_user: dict):
    with pytest.raises(security.HTTPException):
        await security.authenticate_user(registered_user["email"], "Wrong password")


@pytest.mark.anyio
async def test_get_current_user(registered_user: dict):
    token = security.create_access_token(registered_user["email"])
    user = await security.get_authenticated_user(token)
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_current_user_invalid_token():
    with pytest.raises(security.HTTPException):
        await security.get_authenticated_user("Invalid token")


@pytest.mark.anyio
async def test_get_current_user_wrong_type_token(registered_user: dict):
    token = security.create_confirmation_token(registered_user["email"])
    with pytest.raises(security.HTTPException):
        await security.get_authenticated_user(token)
