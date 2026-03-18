"""
Tests for email service functionality
"""
import os
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from app.services.email_service import EmailService

class TestEmailService:
    """Test suite for EmailService."""

    @pytest.fixture
    def email_service(self):
        """Create a test instance of EmailService."""
        # Set test environment variables
        os.environ["FLASK_MAIL_USERNAME"] = "test@example.com"
        os.environ["FLASK_MAIL_PASSWORD"] = "password123"
        return EmailService()

    @pytest.fixture
    def mock_smtp(self):
        """Mock SMTP connection."""
        with patch("smtplib.SMTP") as mock_smtp:
            # Setup mock server instance
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            yield mock_server

    def test_service_initialization(self, email_service):
        """Test that the email service initializes correctly."""
        assert email_service.smtp_username == "test@example.com"
        assert email_service.smtp_password == "password123"
        assert email_service.is_configured == True

    def test_check_configuration_missing_fields(self):
        """Test configuration check when fields are missing."""
        # Clear environment variables
        for key in ["FLASK_MAIL_USERNAME", "FLASK_MAIL_PASSWORD"]:
            if key in os.environ:
                del os.environ[key]

        service = EmailService()
        assert service.is_configured == False

    def test_render_template_success(self, email_service):
        """Test successful template rendering."""
        # Create a mock template for testing
        test_template_dir = Path(__file__).parent / "test_templates"
        test_template_dir.mkdir(exist_ok=True)
        test_template = test_template_dir / "test_template.html"

        with open(test_template, "w") as f:
            f.write("<html><body>Hello, {{ name }}!</body></html>")

        # Override jinja environment to use test template directory
        email_service.jinja_env.loader.searchpath.append(str(test_template_dir))

        # Test rendering
        result = email_service._render_template("test_template.html", {"name": "Test User"})
        assert "Hello, Test User!" in result

        # Cleanup
        test_template.unlink()
        test_template_dir.rmdir()

    def test_render_template_fallback(self, email_service):
        """Test fallback when template rendering fails."""
        # Test with non-existent template
        result = email_service._render_template("nonexistent_template.html",
                                              {"booking_reference": "TEST123", "date": "2023-01-01"})
        assert "TEST123" in result
        assert "2023-01-01" in result

    def test_send_confirmation_email_success(self, email_service, mock_smtp):
        """Test successful email sending."""
        booking_data = {
            "booking_reference": "TEST123",
            "date": "January 1, 2023",
            "time": "10:00 - 11:00",
            "location_name": "Test Office",
            "location_address": "123 Test St",
            "user_name": "Test User"
        }

        # Patch the _render_template method to return a simple string
        with patch.object(email_service, '_render_template', return_value="<html><body>Test Email</body></html>"):
            success, error = email_service.send_confirmation_email("recipient@example.com", booking_data)

        assert success == True
        assert error is None
        # Verify SMTP was called correctly
        mock_smtp.send_message.assert_called_once()

    def test_send_confirmation_email_no_config(self):
        """Test email sending when service is not configured."""
        # Clear environment variables
        for key in ["FLASK_MAIL_USERNAME", "FLASK_MAIL_PASSWORD"]:
            if key in os.environ:
                del os.environ[key]

        service = EmailService()
        success, error = service.send_confirmation_email("recipient@example.com", {})

        assert success == False
        assert "not configured" in error

    @patch("smtplib.SMTP")
    def test_send_confirmation_email_smtp_error(self, mock_smtp, email_service):
        """Test handling of SMTP errors."""
        # Make SMTP raise an exception
        mock_smtp.side_effect = Exception("SMTP Connection Error")

        success, error = email_service.send_confirmation_email("recipient@example.com", {})

        assert success == False
        assert "Failed to send" in error
        assert "SMTP Connection Error" in error
