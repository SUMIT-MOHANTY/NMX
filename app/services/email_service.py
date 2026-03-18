import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
import datetime
from pathlib import Path

from app.core.config import settings

def send_email(
    email_to: str,
    subject: str,
    html_content: str,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None
) -> bool:
    """
    Send an email using the configured SMTP server.

    Args:
        email_to: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
        cc: Carbon copy recipients
        bcc: Blind carbon copy recipients

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        message = MIMEMultipart()
        message["From"] = settings.SMTP_SENDER
        message["To"] = email_to
        message["Subject"] = subject

        if cc:
            message["Cc"] = ", ".join(cc)

        message.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()

            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

            recipients = [email_to]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)

            server.sendmail(settings.SMTP_SENDER, recipients, message.as_string())

        return True

    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_booking_confirmation(
    email: str,
    name: str,
    booking_id: str,
    confirmation_code: str,
    slot_date: datetime.date,
    slot_time: datetime.time,
    office_location: str
) -> bool:
    """
    Send a booking confirmation email.

    Args:
        email: Recipient email address
        name: Recipient name
        booking_id: ID of the booking
        confirmation_code: Booking confirmation code
        slot_date: Date of the appointment
        slot_time: Time of the appointment
        office_location: Location of the appointment

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    subject = f"Passport Appointment Confirmation - {confirmation_code}"

    # Format date and time
    formatted_date = slot_date.strftime("%A, %B %d, %Y")
    formatted_time = slot_time.strftime("%I:%M %p")

    # Email template
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #003366; color: white; padding: 10px 20px; text-align: center; }}
            .content {{ padding: 20px; border: 1px solid #ddd; }}
            .confirmation-box {{ background-color: #f5f5f5; padding: 15px; margin: 20px 0; text-align: center; }}
            .footer {{ font-size: 12px; color: #666; margin-top: 20px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Passport Appointment Confirmation</h1>
            </div>
            <div class="content">
                <p>Dear {name},</p>
                <p>Your passport application appointment has been successfully booked. Please find the details below:</p>

                <div class="confirmation-box">
                    <h2>Booking Details</h2>
                    <p><strong>Confirmation Code:</strong> {confirmation_code}</p>
                    <p><strong>Date:</strong> {formatted_date}</p>
                    <p><strong>Time:</strong> {formatted_time}</p>
                    <p><strong>Location:</strong> {office_location}</p>
                    <p><strong>Booking Reference:</strong> {booking_id}</p>
                </div>

                <p><strong>Important Instructions:</strong></p>
                <ul>
                    <li>Please arrive 15 minutes before your scheduled time.</li>
                    <li>Bring your confirmation code and a valid ID.</li>
                    <li>Bring all required documents for your passport application.</li>
                </ul>

                <p>If you need to cancel or reschedule your appointment, please log in to your account or contact our support team.</p>

                <p>Thank you for using our service.</p>

                <p>Best Regards,<br>Passport Office</p>
            </div>
            <div class="footer">
                <p>This is an automated message, please do not reply to this email.</p>
                <p> {datetime.datetime.now().year} Passport Office. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(
        email_to=email,
        subject=subject,
        html_content=html_content
    )
