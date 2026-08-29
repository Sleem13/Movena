"""Daily integration for private, non-recorded individual appointments."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx

from app.core.config import Settings, get_settings
from app.db.models import Appointment, User


class TelemedicineError(RuntimeError):
    pass


def _request(method: str, path: str, payload: dict, settings: Settings) -> dict:
    try:
        response = httpx.request(
            method, f"https://api.daily.co/v1{path}", json=payload,
            headers={"Authorization": f"Bearer {settings.daily_api_key}"}, timeout=15,
        )
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise TelemedicineError("The secure video provider is temporarily unavailable.") from exc


def ensure_private_room(appointment: Appointment, settings: Settings | None = None) -> str:
    active = settings or get_settings()
    if not active.enable_telemedicine:
        raise TelemedicineError("Video appointments are not enabled.")
    if appointment.daily_room_name:
        return appointment.daily_room_name
    start = appointment.starts_at if appointment.starts_at.tzinfo else appointment.starts_at.replace(tzinfo=timezone.utc)
    end = appointment.ends_at if appointment.ends_at.tzinfo else appointment.ends_at.replace(tzinfo=timezone.utc)
    room_name = f"pv-{appointment.appointment_id}"
    _request("POST", "/rooms", {
        "name": room_name,
        "privacy": "private",
        "properties": {
            "nbf": int((start - timedelta(minutes=15)).timestamp()),
            "exp": int((end + timedelta(minutes=30)).timestamp()),
            "max_participants": 2,
            "enable_recording": "off",
            "start_audio_off": True,
            "start_video_off": True,
            "enable_screenshare": False,
        },
    }, active)
    appointment.daily_room_name = room_name
    return room_name


def create_join_token(
    appointment: Appointment, user: User, is_owner: bool,
    settings: Settings | None = None,
) -> tuple[str, str, datetime]:
    active = settings or get_settings()
    now = datetime.now(timezone.utc)
    start = appointment.starts_at if appointment.starts_at.tzinfo else appointment.starts_at.replace(tzinfo=timezone.utc)
    end = appointment.ends_at if appointment.ends_at.tzinfo else appointment.ends_at.replace(tzinfo=timezone.utc)
    join_at = start - timedelta(minutes=15)
    expires_at = end + timedelta(minutes=30)
    if now < join_at or now > expires_at:
        raise TelemedicineError("The appointment room is available from 15 minutes before the session until 30 minutes after it ends.")
    room_name = ensure_private_room(appointment, active)
    result = _request("POST", "/meeting-tokens", {"properties": {
        "room_name": room_name,
        "user_id": user.user_id,
        "user_name": user.full_name or user.username or "PhysioVision user",
        "is_owner": is_owner,
        "nbf": int(join_at.timestamp()),
        "exp": int(expires_at.timestamp()),
        "enable_recording": False,
        "enable_screenshare": False,
    }}, active)
    token = result.get("token")
    if not token:
        raise TelemedicineError("The secure meeting token could not be created.")
    return f"https://{active.daily_domain}/{room_name}", str(token), expires_at
