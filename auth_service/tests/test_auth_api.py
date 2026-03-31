import pytest


@pytest.mark.asyncio
async def test_register_login_me_flow(client):
    register_response = await client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "Testpass123",
        },
    )

    assert register_response.status_code == 201
    register_data = register_response.json()
    assert register_data["email"] == "user@example.com"
    assert register_data["role"] == "user"
    assert "id" in register_data
    assert "created_at" in register_data

    login_response = await client.post(
        "/auth/login",
        data={
            "username": "user@example.com",
            "password": "Testpass123",
        },
    )

    assert login_response.status_code == 200
    login_data = login_response.json()
    assert login_data["token_type"] == "bearer"
    assert isinstance(login_data["access_token"], str)
    assert len(login_data["access_token"]) > 20

    access_token = login_data["access_token"]

    me_response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == "user@example.com"
    assert me_data["role"] == "user"


@pytest.mark.asyncio
async def test_register_duplicate_user_returns_409(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "Testpass123",
    }

    first_response = await client.post("/auth/register", json=payload)
    second_response = await client.post("/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "User already exists"


@pytest.mark.asyncio
async def test_login_with_wrong_password_returns_401(client):
    await client.post(
        "/auth/register",
        json={
            "email": "wrongpass@example.com",
            "password": "Testpass123",
        },
    )

    login_response = await client.post(
        "/auth/login",
        data={
            "username": "wrongpass@example.com",
            "password": "Wrongpass123",
        },
    )

    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Invalid email or password"