"""Operational administration for assignments, catalog, care, billing, and audit."""

from uuid import uuid4

from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Literal
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_admin, require_super_admin
from app.api.error_responses import api_error_response
from app.db.database import get_db
from app.db.models import (
    Appointment, AuditLog, DataRightsRequest, Order, PackageOffering, PatientProfile, Payment,
    Refund, ServiceOffering, TherapistPatientAssignment, User,
)
from app.schemas.care_schema import (
    AssignmentCreate, AssignmentDetail, PackageOfferingCreate, PackageOfferingDetail,
    RefundCreate, ServiceOfferingCreate, ServiceOfferingDetail,
)
from app.schemas.admin_workflow_schema import AdminWorkflowResponse
from app.services.admin_workflow_service import build_admin_workflow
from app.services.care_service import audit_event, ensure_assignment
from app.services.connection_service import activate, fail
from app.services.paymob_service import PaymentProviderError, refund_transaction

router = APIRouter(
    prefix="/api/v1/admin", tags=["platform-admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("/workflow", response_model=AdminWorkflowResponse)
def workflow(
    queue_limit: int = Query(25, ge=1, le=50),
    actor: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    """Return a de-identified operational snapshot for the protected root workflow."""
    return build_admin_workflow(db, actor_user_id=actor.user_id, queue_limit=queue_limit)


def error(code: str, message: str, status_code: int) -> JSONResponse:
    return api_error_response(code, message, status_code)


@router.post("/assignments", response_model=AssignmentDetail, status_code=status.HTTP_201_CREATED)
def assign(
    data: AssignmentCreate, actor: User = Depends(require_admin), db: Session = Depends(get_db),
):
    if not data.reason or not data.reason.strip():
        fail("An administrative reason is required.", status=422)
    row = activate(db, data.therapist_user_id, data.patient_id, actor, "admin", data.reason.strip())
    db.commit(); db.refresh(row)
    return row


@router.get("/assignments", response_model=list[AssignmentDetail])
def assignments(db: Session = Depends(get_db)):
    return list(db.scalars(select(TherapistPatientAssignment).where(
        TherapistPatientAssignment.status == "active"
    ).order_by(TherapistPatientAssignment.assigned_at.desc())).all())


@router.post("/catalog/services", response_model=ServiceOfferingDetail, status_code=status.HTTP_201_CREATED)
def create_service(
    data: ServiceOfferingCreate, actor: User = Depends(require_admin), db: Session = Depends(get_db),
):
    row = ServiceOffering(service_id=str(uuid4()), currency="EGP", is_active=True, **data.model_dump())
    db.add(row)
    audit_event(db, actor.user_id, "catalog.service_created", "service", row.service_id, {"price_minor": row.price_minor})
    db.commit(); db.refresh(row)
    return row


@router.post("/catalog/packages", response_model=PackageOfferingDetail, status_code=status.HTTP_201_CREATED)
def create_package(
    data: PackageOfferingCreate, actor: User = Depends(require_admin), db: Session = Depends(get_db),
):
    row = PackageOffering(package_id=str(uuid4()), currency="EGP", is_active=True, **data.model_dump())
    db.add(row)
    audit_event(db, actor.user_id, "catalog.package_created", "package", row.package_id, {"price_minor": row.price_minor})
    db.commit(); db.refresh(row)
    return row


@router.get("/appointments")
def appointment_operations(limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)):
    rows = db.scalars(select(Appointment).order_by(Appointment.starts_at.desc()).limit(limit)).all()
    return [{
        "appointment_id": row.appointment_id, "patient_id": row.patient_id,
        "therapist_user_id": row.therapist_user_id, "starts_at": row.starts_at,
        "ends_at": row.ends_at, "status": row.status, "payment_status": row.payment_status,
    } for row in rows]


@router.get("/payments")
def payment_operations(limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)):
    rows = db.execute(select(Payment, Order).join(Order, Payment.order_id == Order.order_id)
                      .order_by(Payment.received_at.desc()).limit(limit)).all()
    return [{
        "payment_id": payment.payment_id, "order_id": order.order_id,
        "amount_minor": payment.amount_minor, "currency": order.currency,
        "status": payment.status, "received_at": payment.received_at,
    } for payment, order in rows]


@router.post("/payments/refunds", status_code=status.HTTP_201_CREATED)
def create_refund(
    data: RefundCreate, actor: User = Depends(require_admin), db: Session = Depends(get_db),
):
    payment = db.scalar(select(Payment).where(Payment.payment_id == data.payment_id).with_for_update())
    if payment is None or payment.status not in {"paid", "partially_refunded"}:
        return error("PAYMENT_NOT_REFUNDABLE", "A refundable payment was not found.", 404)
    refunded = db.scalar(select(func.coalesce(func.sum(Refund.amount_minor), 0)).where(
        Refund.payment_id == payment.payment_id, Refund.status == "completed",
    )) or 0
    if data.amount_minor > payment.amount_minor - refunded:
        return error("REFUND_AMOUNT_INVALID", "Refund exceeds the remaining paid amount.", 409)
    try:
        provider_id = refund_transaction(payment.provider_transaction_id, data.amount_minor)
    except PaymentProviderError as exc:
        return error("REFUND_PROVIDER_UNAVAILABLE", str(exc), 503)
    row = Refund(
        refund_id=str(uuid4()), payment_id=payment.payment_id, amount_minor=data.amount_minor,
        reason=data.reason, status="completed", requested_by_user_id=actor.user_id,
        provider_refund_id=provider_id,
    )
    db.add(row)
    total = refunded + data.amount_minor
    payment.status = "refunded" if total == payment.amount_minor else "partially_refunded"
    audit_event(db, actor.user_id, "payment.refunded", "payment", payment.payment_id, {
        "refund_id": row.refund_id, "amount_minor": data.amount_minor, "reason": data.reason,
    })
    db.commit(); db.refresh(row)
    return {"refund_id": row.refund_id, "payment_id": row.payment_id, "amount_minor": row.amount_minor, "status": row.status}


@router.get("/data-rights-requests")
def privacy_requests(limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)):
    rows = db.scalars(select(DataRightsRequest).order_by(DataRightsRequest.created_at.asc()).limit(limit)).all()
    return [{
        "request_id": row.request_id, "user_id": row.user_id,
        "request_type": row.request_type, "status": row.status,
        "details": row.details, "created_at": row.created_at,
    } for row in rows]


class DataRightsReviewV2(BaseModel):
    decision: Literal["approve", "reject"]
    reason: str = Field(min_length=3, max_length=2000)


def privacy_record(row: DataRightsRequest, account: User) -> dict:
    return {
        "request_id": row.request_id, "request_type": row.request_type,
        "status": row.status, "details": row.details, "created_at": row.created_at,
        "completed_at": row.completed_at, "reviewed_at": row.completed_at,
        "retention_until": None, "account_id": account.user_id,
        "account_email": account.email,
        "account_name": account.full_name or account.username,
    }


@router.get("/platform/data-rights-requests")
def privacy_requests_v2(
    actor: User = Depends(require_super_admin), db: Session = Depends(get_db),
):
    rows = db.execute(select(DataRightsRequest, User).join(
        User, User.user_id == DataRightsRequest.user_id,
    ).order_by(DataRightsRequest.created_at.asc()).limit(500)).all()
    return [privacy_record(row, account) for row, account in rows]


@router.patch("/platform/data-rights-requests/{request_id}")
def resolve_privacy_request_v2(
    request_id: str, data: DataRightsReviewV2,
    actor: User = Depends(require_super_admin), db: Session = Depends(get_db),
):
    result = db.execute(select(DataRightsRequest, User).join(
        User, User.user_id == DataRightsRequest.user_id,
    ).where(DataRightsRequest.request_id == request_id).with_for_update()).first()
    if result is None:
        return error("DATA_RIGHTS_REQUEST_NOT_FOUND", "Privacy request was not found.", 404)
    row, account = result
    if row.status != "pending" or account.is_protected:
        return error("DATA_RIGHTS_REVIEW_DENIED", "This review is unavailable.", 409)
    row.status = "approved" if data.decision == "approve" else "rejected"
    row.resolution_note = data.reason.strip()
    row.completed_at = datetime.now(timezone.utc)
    if data.decision == "approve" and row.request_type == "deletion":
        account.is_active = False
        account.account_status = "suspended"
        account.token_version += 1
    audit_event(db, actor.user_id, "data_rights.reviewed", "data_rights_request", row.request_id, {
        "request_type": row.request_type, "decision": data.decision,
    })
    db.commit(); db.refresh(row)
    return privacy_record(row, account)


@router.patch("/data-rights-requests/{request_id}")
def resolve_privacy_request(
    request_id: str, resolution_note: str = Body(min_length=3, max_length=5000, embed=True),
    actor: User = Depends(require_admin), db: Session = Depends(get_db),
):
    row = db.scalar(select(DataRightsRequest).where(DataRightsRequest.request_id == request_id).with_for_update())
    if row is None:
        return error("DATA_RIGHTS_REQUEST_NOT_FOUND", "Privacy request was not found.", 404)
    row.status = "completed"; row.resolution_note = resolution_note; row.completed_at = datetime.now(timezone.utc)
    audit_event(db, actor.user_id, "data_rights.completed", "data_rights_request", row.request_id, {
        "request_type": row.request_type,
    })
    db.commit()
    return {"request_id": row.request_id, "status": row.status, "completed_at": row.completed_at}


@router.get("/audit")
def audit_log(limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)):
    rows = db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)).all()
    return [{
        "id": row.id, "actor_user_id": row.actor_user_id, "action": row.action,
        "resource_type": row.resource_type, "resource_id": row.resource_id,
        "created_at": row.created_at,
    } for row in rows]


@router.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    return {
        "users": db.scalar(select(func.count()).select_from(User)) or 0,
        "patients": db.scalar(select(func.count()).select_from(PatientProfile)) or 0,
        "active_assignments": db.scalar(select(func.count()).select_from(TherapistPatientAssignment).where(
            TherapistPatientAssignment.status == "active")) or 0,
        "appointments": db.scalar(select(func.count()).select_from(Appointment)) or 0,
        "paid_orders": db.scalar(select(func.count()).select_from(Order).where(Order.status == "paid")) or 0,
    }
