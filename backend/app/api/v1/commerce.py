"""Authenticated checkout and verified Paymob callback APIs."""

from __future__ import annotations

import json
import hashlib
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user, require_role
from app.api.error_responses import api_error_response
from app.core.config import get_settings
from app.db.database import get_db
from app.db.models import Appointment, Order, PackageOffering, PatientProfile, Payment, ServiceOffering, User, utc_now
from app.schemas.auth_schema import UserRole
from app.schemas.care_schema import CheckoutCreate, CheckoutResponse
from app.services.care_service import audit_event
from app.services.paymob_service import PaymentProviderError, create_checkout, verify_webhook_hmac

router = APIRouter(tags=["commerce"])


def error(code: str, message: str, status_code: int) -> JSONResponse:
    return api_error_response(code, message, status_code)


@router.post("/api/v1/checkout", response_model=CheckoutResponse, status_code=status.HTTP_201_CREATED)
def checkout(
    data: CheckoutCreate,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=8, max_length=128),
    actor: User = Depends(require_role(UserRole.patient)), db: Session = Depends(get_db),
):
    scoped_key = hashlib.sha256(f"{actor.user_id}:{idempotency_key}".encode()).hexdigest()
    existing = db.scalar(select(Order).where(
        Order.idempotency_key == scoped_key, Order.user_id == actor.user_id,
    ))
    if existing:
        return CheckoutResponse(
            order_id=existing.order_id, amount_minor=existing.amount_minor,
            currency=existing.currency, status=existing.status,
        )
    product = None
    if data.service_id:
        product = db.scalar(select(ServiceOffering).where(
            ServiceOffering.service_id == data.service_id, ServiceOffering.is_active.is_(True),
        ))
    elif data.package_id:
        product = db.scalar(select(PackageOffering).where(
            PackageOffering.package_id == data.package_id, PackageOffering.is_active.is_(True),
        ))
    if product is None:
        return error("PRODUCT_NOT_FOUND", "The selected service or package is unavailable.", 404)
    if data.appointment_id:
        appointment = db.scalar(select(Appointment).where(Appointment.appointment_id == data.appointment_id))
        if appointment is None:
            return error("APPOINTMENT_NOT_FOUND", "Appointment was not found.", 404)
        patient = db.scalar(select(PatientProfile).where(PatientProfile.user_id == actor.user_id))
        if patient is None or appointment.patient_id != patient.patient_id:
            return error("APPOINTMENT_ACCESS_DENIED", "You cannot pay for this appointment.", 403)
    row = Order(
        order_id=str(uuid4()), user_id=actor.user_id, service_id=data.service_id,
        package_id=data.package_id, appointment_id=data.appointment_id,
        amount_minor=product.price_minor, currency="EGP", status="pending",
        idempotency_key=scoped_key,
    )
    db.add(row); db.flush()
    try:
        paymob_order_id, payment_url = create_checkout(
            row.order_id, row.amount_minor, actor.email,
            actor.full_name or actor.username or "Patient", data.billing_phone,
        )
    except PaymentProviderError as exc:
        db.rollback()
        return error("PAYMENT_PROVIDER_UNAVAILABLE", str(exc), 503)
    row.paymob_order_id = paymob_order_id
    audit_event(db, actor.user_id, "order.created", "order", row.order_id, {
        "amount_minor": row.amount_minor, "currency": row.currency,
    })
    db.commit()
    return CheckoutResponse(
        order_id=row.order_id, amount_minor=row.amount_minor, currency=row.currency,
        status=row.status, payment_url=payment_url,
    )


@router.get("/api/v1/orders")
def orders(
    limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0),
    actor: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    rows = db.scalars(select(Order).where(
        Order.user_id == actor.user_id,
    ).order_by(Order.created_at.desc()).offset(offset).limit(limit)).all()
    return [{
        "order_id": row.order_id, "service_id": row.service_id,
        "package_id": row.package_id, "appointment_id": row.appointment_id,
        "amount_minor": row.amount_minor, "currency": row.currency,
        "status": row.status, "created_at": row.created_at,
    } for row in rows]


@router.post("/api/v1/payments/paymob/webhook")
async def paymob_webhook(
    request: Request, hmac_signature: str = Query(alias="hmac"), db: Session = Depends(get_db),
):
    payload = await request.json()
    obj = payload.get("obj", payload)
    settings = get_settings()
    if not verify_webhook_hmac(obj, hmac_signature, settings.paymob_hmac_secret):
        return error("INVALID_WEBHOOK_SIGNATURE", "Webhook signature is invalid.", 401)
    transaction_id = str(obj.get("id", ""))
    external_order_id = str((obj.get("order") or {}).get("id", ""))
    order = db.scalar(select(Order).where(Order.paymob_order_id == external_order_id).with_for_update())
    if order is None:
        return error("ORDER_NOT_FOUND", "Payment order was not found.", 404)
    amount = int(obj.get("amount_cents", -1))
    currency = str(obj.get("currency", ""))
    if amount != order.amount_minor or currency != order.currency:
        return error("PAYMENT_MISMATCH", "Payment amount or currency does not match the order.", 409)
    payment = db.scalar(select(Payment).where(Payment.provider_transaction_id == transaction_id))
    as_bool = lambda value: value is True or str(value).strip().lower() in {"1", "true", "yes"}
    success = as_bool(obj.get("success")) and not as_bool(obj.get("pending"))
    payment_status = "paid" if success else "failed"
    if payment is None:
        safe_payload = {
            key: obj.get(key) for key in ("id", "amount_cents", "currency", "success", "pending", "created_at")
        }
        payment = Payment(
            payment_id=str(uuid4()), order_id=order.order_id,
            provider_transaction_id=transaction_id, amount_minor=amount,
            status=payment_status, provider_payload_json=json.dumps(safe_payload, sort_keys=True),
        )
        db.add(payment)
    order.status = payment_status
    if success and order.appointment_id:
        appointment = db.scalar(select(Appointment).where(Appointment.appointment_id == order.appointment_id))
        if appointment:
            appointment.payment_status = "paid"
            appointment.status = "confirmed"
    audit_event(db, None, "payment.webhook_processed", "order", order.order_id, {
        "payment_status": payment_status, "provider_transaction_id": transaction_id,
    })
    db.commit()
    return {"status": "accepted"}
