"""Transactional auth email delivery using standard SMTP."""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
from urllib.parse import urlencode

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class EmailDeliveryError(RuntimeError):
    pass


def _send(recipient: str, subject: str, text_body: str, settings: Settings) -> None:
    if settings.email_delivery_mode == "console":
        logger.info("Development email for %s: %s\n%s", recipient, subject, text_body)
        return
    if settings.email_delivery_mode != "smtp" or not settings.smtp_host:
        raise EmailDeliveryError("Transactional email delivery is not configured.")
    message = EmailMessage()
    message["From"] = settings.email_from
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(text_body)
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as client:
            if settings.smtp_use_tls:
                client.starttls()
            if settings.smtp_username:
                client.login(settings.smtp_username, settings.smtp_password)
            client.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        raise EmailDeliveryError("The authentication email could not be delivered.") from exc


def send_verification_email(email: str, token: str, settings: Settings | None = None) -> None:
    active = settings or get_settings()
    link = f"{active.frontend_url}/verify-email?{urlencode({'token': token})}"
    _send(
        email,
        "Verify your PhysioVision email",
        f"Verify your email by opening this time-limited link:\n\n{link}\n\nIf you did not create this account, ignore this email.",
        active,
    )


def send_password_reset_email(email: str, token: str, settings: Settings | None = None) -> None:
    active = settings or get_settings()
    link = f"{active.frontend_url}/reset-password?{urlencode({'token': token})}"
    _send(
        email,
        "Reset your PhysioVision password",
        f"Reset your password by opening this single-use, time-limited link:\n\n{link}\n\nIf you did not request this, ignore this email.",
        active,
    )


def send_care_notification_email(
    email: str, subject: str, body: str, action_url: str | None = None,
    settings: Settings | None = None,
) -> None:
    active = settings or get_settings()
    action = f"\n\nOpen PhysioVision: {active.frontend_url}{action_url}" if action_url else ""
    _send(email, subject, f"{body}{action}\n\nDo not reply with medical information by email.", active)
