import pytest
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_success():
    """Test successful login"""
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "securepassword123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"}
    )

    assert response.status_code == 401
    assert "detail" in response.json()

def test_verify_token():
    """Test token verification"""
    # First login to get a token
    login_response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "securepassword123"}
    )

    token = login_response.json()["access_token"]

    # Verify the token
    response = client.get(
        "/auth/verify",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert "user_id" in response.json()

def test_refresh_token():
    """Test token refresh"""
    # First login to get a refresh token
    login_response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "securepassword123"}
    )

    refresh_token = login_response.json()["refresh_token"]

    # Refresh the token
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

def test_invalid_token():
    """Test with invalid token"""
    response = client.get(
        "/auth/verify",
        headers={"Authorization": "Bearer invalidtoken"}
    )

    assert response.status_code == 401
