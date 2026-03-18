import pytest
from httpx import AsyncClient
from sqlalchemy import select
from backend.app.models.user import User

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, db_session):
    # Test data
    user_data = {
        "full_name": "Test User",
        "email": "test@example.com",
        "mobile": "+1234567890",
        "password": "Password123",
        "confirm_password": "Password123"
    }

    # Send registration request
    response = await client.post("/api/auth/register", json=user_data)

    # Check response
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert data["mobile"] == user_data["mobile"]
    assert "id" in data
    assert "created_at" in data

    # Check if user was saved to database
    result = await db_session.execute(select(User).where(User.email == user_data["email"]))
    user = result.scalars().first()
    assert user is not None
    assert user.email == user_data["email"]
    assert user.full_name == user_data["full_name"]
    assert user.mobile == user_data["mobile"]
    assert user.hashed_password != user_data["password"]  # Password should be hashed

@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, db_session):
    # Create first user
    user_data = {
        "full_name": "Test User",
        "email": "duplicate@example.com",
        "mobile": "+1234567890",
        "password": "Password123",
        "confirm_password": "Password123"
    }

    await client.post("/api/auth/register", json=user_data)

    # Try to create second user with same email
    user_data2 = {
        "full_name": "Another User",
        "email": "duplicate@example.com",  # Same email
        "mobile": "+0987654321",
        "password": "Password123",
        "confirm_password": "Password123"
    }

    response = await client.post("/api/auth/register", json=user_data2)

    # Check error response
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"

@pytest.mark.asyncio
async def test_register_validation(client: AsyncClient):
    # Test with invalid data
    invalid_data = {
        "full_name": "Test User",
        "email": "not-an-email",
        "mobile": "invalid",
        "password": "short",
        "confirm_password": "not-matching"
    }

    response = await client.post("/api/auth/register", json=invalid_data)

    # Check validation error
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
