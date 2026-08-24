"""Authenticated, derived-landmark-only real-time coaching channel."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone

import jwt
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.core.security import decode_access_token
from app.db.database import SessionLocal
from app.db.models import User
from app.services.realtime_coaching_service import (
    MAX_MESSAGE_BYTES,
    MAX_SESSION_SECONDS,
    SUPPORTED_EXERCISES,
    RealtimeExerciseSession,
)


router = APIRouter(prefix="/api/v1/coaching", tags=["coaching"])


@router.get("/readiness")
def coaching_readiness() -> dict:
    return {
        "status": "ready",
        "capabilities": {
            "pose_data_pipeline": True,
            "recognition_models": True,
            "hand_orientation_evidence": True,
            "authenticated_streaming": True,
            "rep_events": True,
            "metadata_persistence": True,
        },
        "supported_realtime_exercises": sorted(SUPPORTED_EXERCISES),
        "transport": "websocket_derived_landmarks_only",
    }


async def _receive_json(websocket: WebSocket, timeout: float | None = None) -> dict:
    receive = websocket.receive_text()
    raw = await asyncio.wait_for(receive, timeout=timeout) if timeout else await receive
    if len(raw.encode("utf-8")) > MAX_MESSAGE_BYTES:
        raise ValueError("MESSAGE_TOO_LARGE")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("INVALID_MESSAGE")
    return value


@router.websocket("/stream")
async def realtime_coaching_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    session: RealtimeExerciseSession | None = None
    db = SessionLocal()
    persisted = False
    try:
        auth = await _receive_json(websocket, timeout=10)
        if auth.get("type") != "authenticate" or not auth.get("token"):
            await websocket.send_json({"type": "error", "code": "AUTH_REQUIRED", "message": "Authenticate before streaming landmarks."})
            await websocket.close(code=4401)
            return
        try:
            payload = decode_access_token(str(auth["token"]))
        except (jwt.PyJWTError, KeyError):
            await websocket.send_json({"type": "error", "code": "INVALID_TOKEN", "message": "The access token is invalid or expired."})
            await websocket.close(code=4401)
            return
        user = db.scalar(select(User).where(User.user_id == payload["sub"]))
        if user is None or not user.is_active or not user.is_verified or payload.get("ver", 0) != user.token_version:
            await websocket.send_json({"type": "error", "code": "INVALID_TOKEN", "message": "The user is unavailable."})
            await websocket.close(code=4403)
            return
        exercise_id = str(auth.get("exercise_id", ""))
        if exercise_id not in SUPPORTED_EXERCISES:
            await websocket.send_json({"type": "error", "code": "UNSUPPORTED_EXERCISE", "message": "Choose a supported live exercise."})
            await websocket.close(code=4400)
            return

        session = RealtimeExerciseSession(user_id=user.user_id, exercise_id=exercise_id)
        await websocket.send_json({
            "type": "session_started", "session_id": session.session_id, "exercise_id": exercise_id,
            "expires_in_seconds": MAX_SESSION_SECONDS, "frames_retained": False,
        })
        while True:
            elapsed = (datetime.now(timezone.utc) - session.started_at).total_seconds()
            if elapsed >= MAX_SESSION_SECONDS:
                await websocket.send_json({"type": "warning", "code": "SESSION_TTL_REACHED", "message": "The real-time session reached its time limit."})
                break
            message = await _receive_json(websocket, timeout=min(30, MAX_SESSION_SECONDS - elapsed))
            if message.get("type") == "stop":
                break
            if message.get("type") != "landmarks":
                await websocket.send_json({"type": "error", "code": "INVALID_MESSAGE", "message": "Only landmark or stop messages are accepted."})
                continue
            for event in session.process_frame(message):
                await websocket.send_json(event)
        summary = session.persist(db)
        persisted = True
        await websocket.send_json(summary)
        await websocket.close(code=1000)
    except (WebSocketDisconnect, asyncio.TimeoutError):
        pass
    except (ValueError, json.JSONDecodeError) as exc:
        await websocket.send_json({"type": "error", "code": str(exc), "message": "The coaching message was rejected."})
        await websocket.close(code=4400)
    finally:
        if session is not None and not persisted:
            session.persist(db)
        db.close()
