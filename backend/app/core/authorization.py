"""Deployment-invariant role permissions stored with each user account."""

from __future__ import annotations

import json


ROLE_PERMISSIONS: dict[str, tuple[str, ...]] = {
    "super_admin": ("*",),
    "admin": (
        "analysis:create", "analysis:read:any", "session:manage:any",
        "patient:manage", "dashboard:therapist",
    ),
    "therapist": (
        "analysis:create", "analysis:read:assigned", "session:manage:assigned",
        "patient:manage:assigned", "dashboard:therapist",
    ),
    "patient": ("analysis:create", "analysis:read:own", "session:manage:own"),
    "support": ("support:account-status", "support:appointments:metadata"),
    "researcher_demo": ("analysis:create", "analysis:read:own", "session:manage:own"),
}


def permissions_for_role(role: str) -> list[str]:
    """Return a stable snapshot so local and deployed accounts receive identical rights."""
    return list(ROLE_PERMISSIONS.get(role, ()))


def permissions_json_for_role(role: str) -> str:
    return json.dumps(permissions_for_role(role), separators=(",", ":"))
