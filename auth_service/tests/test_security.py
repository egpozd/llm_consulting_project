from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_not_equal_plain_password():
    password = "Testpass123"
    password_hash = hash_password(password)

    assert password_hash != password
    assert isinstance(password_hash, str)
    assert len(password_hash) > 20


def test_verify_password_success():
    password = "Testpass123"
    password_hash = hash_password(password)

    assert verify_password(password, password_hash) is True


def test_verify_password_wrong_password():
    password_hash = hash_password("Testpass123")

    assert verify_password("Wrongpass123", password_hash) is False


def test_create_and_decode_access_token():
    token = create_access_token(user_id=123, role="user")
    payload = decode_access_token(token)

    assert payload["sub"] == "123"
    assert payload["role"] == "user"
    assert "iat" in payload
    assert "exp" in payload