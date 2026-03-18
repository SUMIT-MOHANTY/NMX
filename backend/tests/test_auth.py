import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.main import app
from backend.app.models.user import User
from backend.app.db.session import get_db

client = TestClient(app)

def test_register_successful(db: Session):
    # Test data
    user_data = {
        "full_name": "Test User",
        "email": "testuser@example.com",
        "mobile": "+1234567890",
        "password": "password123",
        "confirm_password": "password123"
    }

    # Send request
    response = client.post("/api/auth/register", json=user_data)

    # Assertions
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == user_data["full_name"]
    assert data["email"] == user_data["email"]
    assert data["mobile"] == user_data["mobile"]
    assert "id" in data
    assert "created_at" in data

    # Verify user exists in DB
    db_user = db.query(User).filter(User.email == user_data["email"]).first()
    assert db_user is not None
    assert db_user.full_name == user_data["full_name"]

def test_register_duplicate_email(db: Session):
    # Create a user first
    user_data = {
        "full_name": "Existing User",
        "email": "existing@example.com",
        "mobile": "+0987654321",
        "password": "password123",
        "confirm_password": "password123"
    }
    client.post("/api/auth/register", json=user_data)

    # Try to register with the same email
    response = client.post("/api/auth/register", json=user_data)

    # Assertions for conflict
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"

def test_register_invalid_data():
    # Test with invalid email
    invalid_email_data = {
        "full_name": "Invalid User",
        "email": "not-an-email",
        "mobile": "+1234567890",
        "password": "password123",
        "confirm_password": "password123"
    }
    response = client.post("/api/auth/register", json=invalid_email_data)
    assert response.status_code == 400

    # Test with password mismatch
    password_mismatch_data = {
        "full_name": "Mismatch User",
        "email": "mismatch@example.com",
        "mobile": "+1234567890",
        "password": "password123",
        "confirm_password": "differentpassword"
    }
    response = client.post("/api/auth/register", json=password_mismatch_data)
    assert response.status_code == 400

    # Test with short password
    short_password_data = {
        "full_name": "Short Password User",
        "email": "short@example.com",
        "mobile": "+1234567890",
        "password": "short",
        "confirm_password": "short"
    }
    response = client.post("/api/auth/register", json=short_password_data)
    assert response.status_code == 400
