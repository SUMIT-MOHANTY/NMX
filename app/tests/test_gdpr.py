import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.core.config import settings

client = TestClient(app)

@pytest.fixture
def auth_headers():
    """Generate authentication headers with a test JWT token"""
    # This is a simplified mock for testing
    return {"Authorization": "Bearer test_token"}

def test_export_user_data_unauthorized():
    """Test that unauthenticated requests are rejected"""
    response = client.get("/api/me/export")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

@patch("app.api.routes.gdpr.get_current_user")
@patch("app.api.routes.gdpr.get_user_data_export")
def test_export_user_data_success(mock_export, mock_auth, auth_headers):
    """Test successful data export"""
    # Mock the authenticated user
    mock_user = MagicMock()
    mock_user.id = "test-user-id"
    mock_auth.return_value = mock_user

    # Mock the export data
    mock_export.return_value = {
        "profile": {
            "id": "test-user-id",
            "email": "test@example.com",
            "full_name": "Test User",
            "phone_number": "1234567890",
            "created_at": "2023-01-01T00:00:00",
            "is_active": True
        },
        "bookings": [
            {
                "id": "booking-id-1",
                "slot_id": "slot-id-1",
                "start_time": "2023-02-01T10:00:00",
                "end_time": "2023-02-01T10:30:00",
                "location": "Test Location",
                "status": "confirmed",
                "created_at": "2023-01-15T00:00:00"
            }
        ]
    }

    response = client.get("/api/me/export", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "profile" in data
    assert "bookings" in data
    assert data["profile"]["email"] == "test@example.com"
    assert len(data["bookings"]) == 1

@patch("app.api.routes.gdpr.get_current_user")
@patch("app.api.routes.gdpr.delete_user_account")
def test_delete_user_success(mock_delete, mock_auth, auth_headers):
    """Test successful user deletion"""
    # Mock the authenticated user
    mock_user = MagicMock()
    mock_user.id = "test-user-id"
    mock_auth.return_value = mock_user

    # Mock successful deletion
    mock_delete.return_value = True

    response = client.delete("/api/me", headers=auth_headers)
    assert response.status_code == 204
    assert response.content == b''  # No content returned

    # Verify delete function was called with correct ID
    mock_delete.assert_called_once_with(pytest.ANY, "test-user-id")

def test_delete_user_unauthorized():
    """Test that unauthenticated deletion requests are rejected"""
    response = client.delete("/api/me")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

@patch("app.api.routes.gdpr.get_current_user")
@patch("app.api.routes.gdpr.delete_user_account")
def test_delete_user_failure(mock_delete, mock_auth, auth_headers):
    """Test handling of deletion failure"""
    # Mock the authenticated user
    mock_user = MagicMock()
    mock_user.id = "test-user-id"
    mock_auth.return_value = mock_user

    # Mock failed deletion
    mock_delete.return_value = False

    response = client.delete("/api/me", headers=auth_headers)
    assert response.status_code == 500
    assert "Failed to delete user account" in response.json()["detail"]
