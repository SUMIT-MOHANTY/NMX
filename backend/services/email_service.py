"""
Email service for sending transactional emails to users.

This module provides functionality for sending confirmation emails
after successful booking completions.
"""
import os
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from jinja2 import Environment, FileSystemLoader

# Set up logging
logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending transactional emails to users."""

    def __init__(self):
        """Initialize the email service with configuration from environment variables."""
        self.smtp_server = os.getenv("FLASK_MAIL_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("FLASK_MAIL_PORT", 587))
        self.smtp_username = os.getenv("FLASK_MAIL_USERNAME", "")
        self.smtp_password = os.getenv("FLASK_MAIL_PASSWORD", "")
        self.sender_email = os.getenv("FLASK_MAIL_DEFAULT_SENDER", "passport@example.com")
        self.use_tls = os.getenv("FLASK_MAIL_USE_TLS", "True").lower() == "true"

        # Configure template environment
        template_dir = Path(__file__).parent.parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))

        # Check if email configuration is available
        self.is_configured = self._check_configuration()

    def _check_configuration(self) -> bool:
        """
        Verify that the email service is properly configured.

        Returns:
            bool: True if configuration is complete, False otherwise
        """
        required_fields = ["FLASK_MAIL_USERNAME", "FLASK_MAIL_PASSWORD"]
        for field in required_fields:
            if not os.getenv(field):
                logger.warning(f"Email service missing required config: {field}")
                return False
        return True

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render an email template with the given context.

        Args:
            template_name: Name of the template file
            context: Dictionary with variables for template rendering

        Returns:
            str: Rendered HTML content
        """
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Template rendering error: {str(e)}")
            # Fallback to basic template in case of error
            return f"""
            <html>
                <body>
                    <h1>Booking Confirmation</h1>
                    <p>Your booking has been confirmed.</p>
                    <p>Reference: {context.get('booking_reference', 'N/A')}</p>
                    <p>Date: {context.get('date', 'N/A')}</p>
                    <p>Time: {context.get('time', 'N/A')}</p>
                </body>
            </html>
            """

    def send_confirmation_email(self,
                               recipient_email: str,
                               booking_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Send a booking confirmation email to the user.

        Args:
            recipient_email: User's email address
            booking_data: Dictionary containing booking details including:
                - booking_reference: Unique booking reference
                - date: Appointment date
                - time: Appointment time
                - location_name: Name of passport office location
                - location_address: Address of passport office
                - user_name: Full name of the user

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if not self.is_configured:
            logger.warning("Email service not properly configured. Skipping email send.")
            return False, "Email service not configured"

        if not recipient_email:
            logger.error("No recipient email provided")
            return False, "No recipient email provided"

        try:
            # Create the email message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"Passport Appointment Confirmation - {booking_data.get('booking_reference', '')}"

            # Render the email template
            html_content = self._render_template("booking_confirmation.html", booking_data)
            msg.attach(MIMEText(html_content, 'html'))

            # Connect to SMTP server and send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Confirmation email sent successfully to {recipient_email}")
            return True, None

        except Exception as e:
            error_msg = f"Failed to send confirmation email: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

# Singleton instance for app-wide use
email_service = EmailService()
