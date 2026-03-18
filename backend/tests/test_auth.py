import pytest
from fastapi.testclient import TestClient
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data
test_user = {
    "email": "test@example.com",
    "password": "Password123",
    "full_name": "Test User"
}

def test_register_user(client):
    """Test user registration"""
    try:
        response = client.post("/api/auth/register", json=test_user)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user["email"]
        assert "id" in data
        assert "hashed_password" not in data
        logger.info("User registration test passed")
    except Exception as e:
        logger.error(f"User registration test failed: {e}")
        raise

def test_register_duplicate_user(client):
    """Test duplicate user registration fails"""
    try:
        # First registration
        client.post("/api/auth/register", json=test_user)

        # Duplicate registration should fail
        response = client.post("/api/auth/register", json=test_user)
        assert response.status_code == 400
        logger.info("Duplicate user registration test passed")
    except Exception as e:
        logger.error(f"Duplicate user registration test failed: {e}")
        raise

def test_login_user(client):
    """Test user login"""
    try:
        # Register user first
        client.post("/api/auth/register", json=test_user)

        # Login
        response = client.post(
            "/api/auth/login",
            data={"username": test_user["email"], "password": test_user["password"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        logger.info("User login test passed")
    except Exception as e:
        logger.error(f"User login test failed: {e}")
        raise

def test_login_wrong_password(client):
    """Test login with wrong password"""
    try:
        # Register user first
        client.post("/api/auth/register", json=test_user)

        # Login with wrong password
        response = client.post(
            "/api/auth/login",
            data={"username": test_user["email"], "password": "wrongpassword"}
        )
        assert response.status_code == 401
        logger.info("Wrong password login test passed")
    except Exception as e:
        logger.error(f"Wrong password login test failed: {e}")
        raise

def test_get_user_me(client):
    """Test getting current user profile"""
    try:
        # Register user
        client.post("/api/auth/register", json=test_user)

        # Login
        response = client.post(
            "/api/auth/login",
            data={"username": test_user["email"], "password": test_user["password"]}
        )
        token = response.json()["access_token"]

        # Get profile
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user["email"]
        logger.info("Get user profile test passed")
    except Exception as e:
        logger.error(f"Get user profile test failed: {e}")
        raise
