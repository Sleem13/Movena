"""Load and interpret exercise-reference JSON documents.

Provides a minimal API to load and flatten the reference data into a
model-friendly list of programs. It can infer injury-specific action
guidance from the reference condition text and support weighted
suggestions for exercise-based pretraining.
"""

from pathlib import Path
import json
import re
from typing import Any, Dict, List, Optional

from rehabrl.config import INJURY_TYPES
from rehabrl.data.exercise_database import ACTION_SPACE


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower()).strip()


def _flatten_strings(value: Any) -> List[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        result: List[str] = []
        for v in value.values():
            result.extend(_flatten_strings(v))
        return result
    if isinstance(value, list):
        result = []
        for item in value:
            result.extend(_flatten_strings(item))
        return result
    return []


def _entry_text(entry: Dict[str, Any]) -> str:
    parts: List[str] = []
    if "condition" in entry and isinstance(entry["condition"], str):
        parts.append(entry["condition"])
    if "name" in entry and isinstance(entry["name"], str):
        parts.append(entry["name"])
    if "program" in entry and isinstance(entry["program"], dict):
        parts.extend(_flatten_strings(entry["program"]))
    if "raw" in entry:
        parts.extend(_flatten_strings(entry["raw"]))
    return _normalize_text(" ".join(parts))


def _infer_tags(text: str) -> Dict[str, Optional[Any]]:
    stage = None
    intensity = None
    progression = None

    stage_markers = [
        (
            0,
            [
                "acute",
                "phase 0",
                "week 1",
                "week 2",
                "early",
                "postpartum",
                "pregnancy",
                "immediate after catheter removal",
            ],
        ),
        (
            1,
            [
                "subacute",
                "phase 1",
                "week 3",
                "week 4",
                "weekly sessions",
                "home exercises",
                "low intensity",
                "low-intensity",
            ],
        ),
        (
            2,
            [
                "remodeling",
                "phase 2",
                "week 6",
                "week 8",
                "moderate",
                "functional progression",
            ],
        ),
        (
            3,
            [
                "functional",
                "phase 3",
                "return",
                "sport-specific",
                "plyometric",
                "agility",
                "power",
                "high-intensity",
            ],
        ),
        (4, ["return", "maintenance", "long-term", "sport", "high-level"]),
    ]
    for idx, markers in stage_markers:
        if any(marker in text for marker in markers):
            stage = idx
            break

    if any(
        word in text
        for word in [
            "high intensity",
            "intensive",
            "advanced",
            "progressive",
            "power",
            "plyometric",
        ]
    ):
        intensity = "High"
    elif any(
        word in text
        for word in [
            "moderate",
            "moderate intensity",
            "3x",
            "weekly",
            "strength training",
            "electrical stimulation",
        ]
    ):
        intensity = "Moderate"
    elif any(
        word in text
        for word in ["low", "gentle", "light", "daily", "easy", "teach", "teaching"]
    ):
        intensity = "Low"

    if any(
        word in text
        for word in [
            "progress",
            "advance",
            "increase",
            "upgrade",
            "graduated",
            "return to sport",
            "functional progression",
        ]
    ):
        progression = "Progress"
    elif any(
        word in text
        for word in [
            "maintain",
            "maintenance",
            "keep",
            "stay",
            "same intensity",
            "stabilize",
        ]
    ):
        progression = "Maintain"
    elif any(
        word in text
        for word in ["reduce", "regress", "rest", "avoid", "lower", "gentle"]
    ):
        progression = "Regress"

    return {
        "stage": stage,
        "intensity": intensity,
        "progression": progression,
    }


def _infer_injury_types(text: str) -> List[str]:
    matches: List[str] = []
    normalized = _normalize_text(text)
    for injury in INJURY_TYPES:
        injury_key = _normalize_text(injury)
        if injury_key and all(word in normalized for word in injury_key.split()):
            matches.append(injury)
    return matches


def _condition_matches(
    preferred_condition: str, entry_condition: Optional[str], entry_text: str
) -> bool:
    normalized_target = _normalize_text(preferred_condition)
    if not normalized_target:
        return False

    if entry_condition:
        entry_condition_norm = _normalize_text(entry_condition)
        if normalized_target == entry_condition_norm:
            return True
        if (
            normalized_target in entry_condition_norm
            or entry_condition_norm in normalized_target
        ):
            return True

    if normalized_target in entry_text:
        return True

    for injury in _infer_injury_types(entry_text):
        if _normalize_text(injury) == normalized_target:
            return True

    return False


def _action_has_injury_match(action, condition_text: Optional[str], text: str) -> bool:
    if not condition_text:
        return False

    cond_norm = _normalize_text(condition_text)
    target_injuries = {
        inj.lower()
        for ex in action.exercises
        for inj in ex.target_injuries
        if inj.lower() != "all"
    }

    for injury in target_injuries:
        injury_key = _normalize_text(injury)
        if injury_key and all(word in cond_norm for word in injury_key.split()):
            return True
        if injury_key and injury_key in text:
            return True

    return False


def _score_prescription(
    action: Any,
    tags: Dict[str, Optional[Any]],
    text: str,
    condition_text: Optional[str] = None,
    inferred_injuries: Optional[List[str]] = None,
) -> float:
    score = 0.0

    if tags["stage"] is not None:
        if action.stage == tags["stage"]:
            score += 5.0  # stronger preference for exact stage match
        elif abs(action.stage - tags["stage"]) == 1:
            score += 2.0  # moderate preference for adjacent stage

    if tags["intensity"] is not None:
        if action.intensity == tags["intensity"]:
            score += 1.5
        elif tags["intensity"] == "Moderate" and action.intensity in (
            "Low",
            "Moderate",
        ):
            score += 0.8
        elif tags["intensity"] == "Low" and action.intensity == "Moderate":
            score += 0.3

    if tags["progression"] is not None:
        if action.progression == tags["progression"]:
            score += 1.0
        elif action.progression == "Maintain" and tags["progression"] == "Progress":
            score += 0.3

    if condition_text and _action_has_injury_match(action, condition_text, text):
        score += 5.0  # higher weight for direct injury condition match

    if inferred_injuries:
        action_injury_matches = {
            inj.lower() for ex in action.exercises for inj in ex.target_injuries
        }
        for injury in inferred_injuries:
            if injury.lower() in action_injury_matches:
                score += 3.0  # increased weight for inferred injury matches

    if "strength training" in text or "high intensity" in text:
        if action.intensity == "High":
            score += 0.5

    return score


def load_exercise_refs(dir_path: str) -> List[Dict[str, Any]]:
    base = Path(dir_path)
    if not base.exists() or not base.is_dir():
        return []

    entries: List[Dict[str, Any]] = []
    for p in sorted(base.glob("*.json")):
        try:
            doc = _load_json(p)
        except Exception:
            continue

        programs = doc.get("therapy_programs") or doc.get("therapy_programs_and_cases")
        if not programs:
            entries.append({"source_file": str(p), "raw": doc})
            continue

        if isinstance(programs, dict):
            programs_list = list(programs.values())
        else:
            programs_list = programs

        for prog in programs_list:
            entry: Dict[str, Any] = {"source_file": str(p), "program": prog}
            if isinstance(prog, dict):
                entry.setdefault(
                    "condition",
                    prog.get("condition")
                    or prog.get("title")
                    or prog.get("chapter")
                    or prog.get("name"),
                )
                entry.setdefault(
                    "name",
                    prog.get("title")
                    or prog.get("case_title")
                    or prog.get("condition")
                    or prog.get("name"),
                )
            entries.append(entry)

    return entries


def summarize_entries(entries: List[Dict[str, Any]]) -> str:
    return f"exercise_refs: {len(entries)} programs loaded"


def build_action_priors(
    entries: List[Dict[str, Any]],
    preferred_condition: Optional[str] = None,
    recovery_stage: Optional[int] = None,
) -> List[float]:
    if not entries:
        return [1.0 for _ in ACTION_SPACE]

    scores = [0.0 for _ in ACTION_SPACE]

    filtered_entries = []
    if preferred_condition:
        for entry in entries:
            entry_condition = entry.get("condition")
            entry_text = _entry_text(entry)
            if _condition_matches(preferred_condition, entry_condition, entry_text):
                filtered_entries.append(entry)
        if not filtered_entries:
            filtered_entries = entries
    else:
        filtered_entries = entries

    for entry in filtered_entries:
        text = _entry_text(entry)
        tags = _infer_tags(text)
        condition_text = preferred_condition or entry.get("condition")
        inferred_injuries = _infer_injury_types(condition_text or text)

        for action in ACTION_SPACE:
            if recovery_stage is not None and abs(action.stage - recovery_stage) > 1:
                continue
            scores[action.action_id] += _score_prescription(
                action,
                tags,
                text,
                condition_text=condition_text,
                inferred_injuries=inferred_injuries,
            )

    total = sum(scores)
    if total <= 0:
        return [1.0 for _ in ACTION_SPACE]

    return [float(score / total) for score in scores]


def get_action_suggestions(
    entries: List[Dict[str, Any]],
    preferred_condition: Optional[str] = None,
    recovery_stage: Optional[int] = None,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    priors = build_action_priors(
        entries, preferred_condition=preferred_condition, recovery_stage=recovery_stage
    )
    ranked = sorted(
        [(idx, score, ACTION_SPACE[idx].name) for idx, score in enumerate(priors)],
        key=lambda item: item[1],
        reverse=True,
    )
    return [
        {"action_id": int(idx), "score": float(score), "name": name}
        for idx, score, name in ranked[:top_k]
    ]
