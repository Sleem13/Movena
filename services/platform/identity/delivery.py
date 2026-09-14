"""Synchronous recovery delivery; plaintext exists only for the outbound call."""
from urllib.parse import urlencode
from django.conf import settings
from django.core.mail import send_mail
from . import sessions


class DeliveryFailed(RuntimeError):
    pass


def recovery_link(purpose, token):
    page = 'verify-email' if purpose == 'verification' else 'reset-password'
    return f"{settings.FRONTEND_URL}/{page}?{urlencode({'token': token})}"


def deliver_recovery(delivery):
    if not delivery:
        return False
    purpose = delivery['purpose']
    if purpose not in {'verification', 'reset'}:
        raise DeliveryFailed()
    subject = 'Verify your Movena account' if purpose == 'verification' else 'Reset your Movena password'
    action = 'Verify your account' if purpose == 'verification' else 'Reset your password'
    body = f"{action}: {recovery_link(purpose, delivery['token'])}\n\nIf you did not request this, ignore this message."
    try:
        sent = send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [delivery['email']], fail_silently=False)
        if sent != 1:
            raise RuntimeError('Delivery was not accepted')
    except Exception as exc:
        sessions.delivery_failed(delivery['user_id'], delivery['token'], purpose)
        raise DeliveryFailed() from exc
    return True
