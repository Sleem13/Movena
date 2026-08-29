"""Server-only Paymob adapter and deterministic webhook verification."""

from __future__ import annotations

import hashlib
import hmac
from typing import Any

import httpx

from app.core.config import Settings, get_settings


PAYMOB_BASE_URL = "https://accept.paymob.com/api"
HMAC_FIELDS = (
    "amount_cents", "created_at", "currency", "error_occured",
    "has_parent_transaction", "id", "integration_id", "is_3d_secure",
    "is_auth", "is_capture", "is_refunded", "is_standalone_payment",
    "is_voided", "order.id", "owner", "pending", "source_data.pan",
    "source_data.sub_type", "source_data.type", "success",
)


class PaymentProviderError(RuntimeError):
    pass


def _nested(payload: dict[str, Any], path: str) -> Any:
    value: Any = payload
    for part in path.split("."):
        value = value.get(part, "") if isinstance(value, dict) else ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return value if value is not None else ""


def verify_webhook_hmac(payload: dict[str, Any], signature: str, secret: str) -> bool:
    message = "".join(str(_nested(payload, field)) for field in HMAC_FIELDS)
    expected = hmac.new(secret.encode(), message.encode(), hashlib.sha512).hexdigest()
    return bool(signature) and hmac.compare_digest(expected, signature.lower())


def _post(path: str, payload: dict, settings: Settings) -> dict:
    try:
        response = httpx.post(f"{PAYMOB_BASE_URL}{path}", json=payload, timeout=20)
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise PaymentProviderError("The payment provider is temporarily unavailable.") from exc


def auth_token(settings: Settings) -> str:
    token = _post("/auth/tokens", {"api_key": settings.paymob_api_key}, settings).get("token")
    if not token:
        raise PaymentProviderError("Paymob authentication failed.")
    return str(token)


def create_checkout(
    merchant_order_id: str, amount_minor: int, billing_email: str,
    billing_name: str, billing_phone: str, settings: Settings | None = None,
) -> tuple[str, str]:
    active = settings or get_settings()
    if not active.enable_payments:
        raise PaymentProviderError("Online payments are not enabled.")
    token = auth_token(active)
    external_order = _post("/ecommerce/orders", {
        "auth_token": token, "delivery_needed": False, "amount_cents": amount_minor,
        "currency": "EGP", "merchant_order_id": merchant_order_id, "items": [],
    }, active)
    paymob_order_id = str(external_order.get("id", ""))
    if not paymob_order_id:
        raise PaymentProviderError("Paymob did not create the order.")
    names = (billing_name or "Patient").split(maxsplit=1)
    payment_key = _post("/acceptance/payment_keys", {
        "auth_token": token, "amount_cents": amount_minor, "expiration": 3600,
        "order_id": paymob_order_id,
        "billing_data": {
            "apartment": "NA", "email": billing_email, "floor": "NA",
            "first_name": names[0], "street": "NA", "building": "NA",
            "phone_number": billing_phone, "shipping_method": "NA",
            "postal_code": "NA", "city": "Cairo", "country": "EG",
            "last_name": names[1] if len(names) > 1 else "Patient", "state": "Cairo",
        },
        "currency": "EGP", "integration_id": int(active.paymob_integration_id),
    }, active).get("token")
    if not payment_key:
        raise PaymentProviderError("Paymob did not create the payment key.")
    return paymob_order_id, f"https://accept.paymob.com/api/acceptance/iframes/{active.paymob_iframe_id}?payment_token={payment_key}"


def refund_transaction(
    provider_transaction_id: str, amount_minor: int, settings: Settings | None = None,
) -> str:
    active = settings or get_settings()
    if not active.enable_payments:
        raise PaymentProviderError("Online payments are not enabled.")
    result = _post("/acceptance/void_refund/refund", {
        "auth_token": auth_token(active),
        "transaction_id": provider_transaction_id,
        "amount_cents": amount_minor,
    }, active)
    if not result.get("success"):
        raise PaymentProviderError("Paymob did not approve the refund.")
    return str(result.get("id") or result.get("transaction_id") or provider_transaction_id)
