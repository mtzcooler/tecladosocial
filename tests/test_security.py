from jose import jwt
from app import security


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
