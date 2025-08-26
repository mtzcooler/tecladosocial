import pytest
from app import security


@pytest.mark.asyncio
def test_password_hashes():
    password = "password"
    assert security.verify_password(password, security.get_password_hash(password))
