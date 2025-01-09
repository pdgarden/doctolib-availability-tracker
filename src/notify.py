import smtplib
import ssl

from loguru import logger

from src.configuration import config


def send_email(receiver_email: str, message: str) -> None:
    """Send email using gmail."""
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(config.sender_email, config.sender_gmail_password.get_secret_value())
        server.sendmail(config.sender_email, receiver_email, message)
    logger.debug(f"Email sent to {receiver_email}")
