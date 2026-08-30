"""Privacy-minimized governance records for RehabRL clinical decisions."""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import AuditLog, User
from app.services.care_service import audit_event


REHAB_DECISION_ACTION = "rehab_rl.decision_generated"


def record_rehab_decision(
    db: Session,
    actor: User,
    request: object,
    result: dict,
    model_contract: dict,
) -> str:
    """Persist a traceable decision summary without patient identifiers or raw measurements."""
    decision_id = str(uuid4())
    safety_screen = getattr(request, "safety_screen")
    clinical_safety = result.get("clinical_safety", {})
    protocol = result.get("protocol", {})
    audit_event(
        db,
        actor.user_id,
        REHAB_DECISION_ACTION,
        "rehab_rl_decision",
        decision_id,
        {
            "condition_id": protocol.get("id") or getattr(request, "condition_id", None),
            "mode": result.get("mode"),
            "source": result.get("source"),
            "action_id": result.get("action_id"),
            "recovery_stage": getattr(request, "recovery_stage", None),
            "treatment_readiness": clinical_safety.get("treatment_readiness"),
            "red_flags_reviewed": safety_screen.red_flags_reviewed,
            "red_flags_present": safety_screen.red_flags_present,
            "precautions_reviewed": safety_screen.precautions_reviewed,
            "postoperative": safety_screen.postoperative,
            "procedure_orders_confirmed": safety_screen.procedure_orders_confirmed,
            "clinician_attestation": safety_screen.clinician_attestation,
            "model_contract_version": model_contract.get("version"),
            "model_contract_fingerprint": model_contract.get("sha256"),
        },
    )
    db.commit()
    return decision_id


def rehab_governance_summary(db: Session, actor: User, days: int = 30) -> dict:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    statement = select(AuditLog).where(
        AuditLog.action == REHAB_DECISION_ACTION,
        AuditLog.created_at >= cutoff,
    )
    scope = "platform" if actor.role == "super_admin" else "clinician"
    if scope == "clinician":
        statement = statement.where(AuditLog.actor_user_id == actor.user_id)
    rows = db.scalars(statement.order_by(AuditLog.created_at.desc()).limit(500)).all()

    readiness: Counter[str] = Counter()
    modes: Counter[str] = Counter()
    recent = []
    for row in rows:
        try:
            metadata = json.loads(row.metadata_json or "{}")
        except (TypeError, json.JSONDecodeError):
            metadata = {}
        readiness[str(metadata.get("treatment_readiness") or "unknown")] += 1
        modes[str(metadata.get("mode") or "unknown")] += 1
        if len(recent) < 10:
            recent.append({
                "decision_id": row.resource_id,
                "created_at": row.created_at,
                "condition_id": metadata.get("condition_id"),
                "mode": metadata.get("mode"),
                "treatment_readiness": metadata.get("treatment_readiness"),
            })

    settings = get_settings()
    return {
        "scope": scope,
        "window_days": days,
        "decisions": len(rows),
        "safety_holds": sum(count for key, count in readiness.items() if key != "ready"),
        "referrals": readiness.get("hold_and_refer", 0),
        "modes": dict(sorted(modes.items())),
        "readiness": dict(sorted(readiness.items())),
        "last_decision_at": rows[0].created_at if rows else None,
        "recent": recent,
        "audit": {
            "enabled": True,
            "privacy_profile": "No patient identifiers, free text, or raw clinical measurements",
            "retention_policy": "Governed by the platform audit-log retention policy",
        },
        "escalation": {
            "configured": bool(settings.clinical_escalation_contact.strip()),
            "organization": settings.clinical_organization_name,
            "contact": settings.clinical_escalation_contact,
            "instruction": settings.clinical_escalation_instruction,
        },
    }
