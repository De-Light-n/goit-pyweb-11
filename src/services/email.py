from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import config

conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_USERNAME,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME="RestAPI Mail",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    The function `send_email` sends an email with a verification token to a specified email address for
    confirmation.
    
    :param email: The `send_email` function takes in three parameters:
    :type email: EmailStr
    :param username: The `username` parameter in the `send_email` function is a string that represents
    the username of the recipient to whom the email will be sent. It is used in the email template to
    personalize the message for the recipient
    :type username: str
    :param host: The `host` parameter in the `send_email` function likely refers to the host or domain
    name of the website or application from which the email is being sent. It is used in the email
    template to provide a link or reference back to the host for actions like email verification or
    account activation
    :type host: str
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)