import logging
from typing import Dict, Any, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings

logger = logging.getLogger("email_service")

class EmailService:
    @staticmethod
    async def send_email(
        recipient_email: str,
        subject: str,
        body: str,
        template_name: Optional[str] = None,
        template_vars: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send an email to a recipient

        Args:
            recipient_email: Email address of the recipient
            subject: Email subject
            body: Plain text body if no template provided
            template_name: Optional template file name
            template_vars: Optional variables for the template

        Returns:
            bool: True if the email was sent successfully, False otherwise
        """
        try:
            message = MIMEMultipart()
            message['From'] = settings.SMTP_SENDER_EMAIL
            message['To'] = recipient_email
            message['Subject'] = subject

            # Use template if provided, otherwise use plain body
            if template_name and template_vars:
                # Simple template implementation
                with open(f"app/templates/{template_name}", "r") as template_file:
                    template_content = template_file.read()

                for key, value in template_vars.items():
                    template_content = template_content.replace(f"{{{{{key}}}}}", str(value))

                message.attach(MIMEText(template_content, 'html'))
            else:
                message.attach(MIMEText(body, 'plain'))

            # Connect to SMTP server and send email
            if settings.ENVIRONMENT == "development":
                logger.info(f"[DEV] Email would be sent to {recipient_email}: {subject}")
                return True

            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(message)

            logger.info(f"Email sent successfully to {recipient_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
            return False

    @staticmethod
    async def send_account_deletion_confirmation(email: str, user_name: str) -> bool:
        """Send confirmation email for account deletion"""
        subject = "Account Deletion Confirmation - Passport Appointment System"
        body = f"""Dear {user_name},

Your account has been successfully deleted from our Passport Appointment Booking System.

Please note that some data may be retained for up to 14 days for backup purposes before permanent deletion,
in accordance with our data retention policy.

If you have any questions or concerns, please contact our support team.

Regards,
The Passport Appointment System Team
"""
        return await EmailService.send_email(email, subject, body)
