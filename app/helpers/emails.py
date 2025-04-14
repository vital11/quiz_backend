from dataclasses import dataclass
from typing import Any

import emails

from jinja2 import Template
from loguru import logger
from pydantic import EmailStr

from app.core.config import settings, BASE_DIR


@dataclass
class EmailData:
    html_content: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template = (
        BASE_DIR / "app" / "email-templates" / "build" / template_name
    ).read_text()
    return Template(source=template).render(context)


def send_email(
    email_to: str | EmailStr,
    subject: str = "",
    html_content: str = "",
) -> None:
    assert settings.smtp.emails_enabled, "no provided configuration for email variables"
    message = emails.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.smtp.EMAILS_FROM_NAME, settings.smtp.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.smtp.HOST, "port": settings.smtp.PORT}
    if settings.smtp.TLS:
        smtp_options["tls"] = True
    elif settings.smtp.SSL:
        smtp_options["ssl"] = True
    if settings.smtp.USER:
        smtp_options["user"] = settings.smtp.USER
    if settings.smtp.PASSWORD:
        smtp_options["password"] = settings.smtp.PASSWORD

    response = message.send(to=email_to, smtp=smtp_options)
    logger.info(f"Send email result: {response}")


def generate_reset_password_email(email_to: str, email: str, token: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email!r}"
    link = (
        f"{settings.FRONTEND_HOST}{settings.api.v1.LOGIN}/reset-password?token={token}"
    )
    html_content = render_email_template(
        template_name="reset_password.html",
        context=dict(
            project_name=project_name,
            username=email,
            email=email_to,
            valid_hours=settings.jwt.RESET_PASSWORD_TOKEN_EXPIRE_HOURS,
            link=link,
        ),
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_new_account_email(
    email_to: str | EmailStr, username: str | EmailStr, password: str
) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username!r}"
    html_content = render_email_template(
        template_name="new_account.html",
        context=dict(
            project_name=project_name,
            username=username,
            password=password,
            email=email_to,
            link=settings.FRONTEND_HOST,
        ),
    )
    return EmailData(html_content=html_content, subject=subject)
