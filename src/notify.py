import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from loguru import logger

from src.configuration import config


def send_email(receiver_email: str, subject: str, message_txt: str, message_html: str) -> None:
    """Send email using SMTP."""
    port = 465  # For SSL
    smtp_server = config.smtp_server

    # Create the email
    msg = MIMEMultipart("alternative")
    msg["From"] = config.sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    # Attach the message to the email
    msg.attach(MIMEText(message_txt, "plain"))
    msg.attach(MIMEText(message_html, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(config.sender_email, config.sender_gmail_password.get_secret_value())
        server.sendmail(config.sender_email, receiver_email, msg.as_string())
    logger.debug(f"Email sent to {receiver_email}")


if __name__ == "__main__":
    send_email(config.receiver_email, "Test", "This is a test email.")
