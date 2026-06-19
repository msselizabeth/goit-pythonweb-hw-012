from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from app.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_verification_email(email: EmailStr, host: str, token: str):
    
    verification_link = f"{host}auth/verify/{token}"
    
    html_content = f"""
    <p>Thank you for registering. Please verify your email by clicking the link below:</p>
    <a href="{verification_link}">Verify Email Address</a>
    """
    
    message = MessageSchema(
        subject="Confirm your email address",
        recipients=[email],
        body=html_content,
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)

async def send_password_reset_email(email: EmailStr, host: str, token: str):
    reset_link = f"{host}auth/reset-password/{token}"
    html_content = f"""
    <p>Please reset your password by clicking the link below:</p>
    <a href="{reset_link}">Reset Password</a>
    """
    message = MessageSchema(
        subject="reset you password",
        recipients=[email],
        body=html_content,
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)