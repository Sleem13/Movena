"""Create a conservative hip-abduction candidate registry for manual review."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

DEFAULT_INPUT = Path("data/processed/registry/unified_samples.csv")
DEFAULT_OUTPUT = Path("data/processed/labels/hip_abduction_training_candidates.csv")
OUTPUT_COLUMNS = ["sample_id", "dataset_name", "file_path", "modality", "exercise_id", "raw_label", "normalized_label", "participant_id", "session_id", "view_type", "recording_quality", "requires_manual_review", "training_ready", "candidate_reason", "notes"]
STRONG_TERMS = ("hip_abduction", "hip abduction", "hip-abduction", "standing hip abduction", "side leg raise", "lateral leg raise")


def _is_candidate(row: dict[str, str]) -> tuple[bool, str]:
    if row.get("exercise_id", "").strip().lower() == "hip_abduction":
        return True, "explicit_exercise_id"
    searchable = " | ".join(row.get(field, "").strip().lower() for field in ("raw_label", "normalized_label", "file_path"))
    match = next((term for term in STRONG_TERMS if term in searchable), None)
    return match is not None, f"strong_text_match:{match}" if match else ""


def prepare_candidates(input_path: Path, output_path: Path) -> list[dict[str, str]]:
    rows = []
    if input_path.exists():
        with input_path.open("r", encoding="utf-8-sig", newline="") as source:
            for row in csv.DictReader(source):
                matches, reason = _is_candidate(row)
                if not matches:
                    continue
                rows.append({column: row.get(column, "") for column in OUTPUT_COLUMNS} | {"exercise_id": "hip_abduction", "requires_manual_review": "true", "training_ready": "false", "candidate_reason": reason, "notes": "Candidate only; exercise identity, view, rep count, and label require human review."})
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Hip-abduction candidates: {len(rows)}")
    print(f"Saved: {output_path}")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    prepare_candidates(args.input, args.output)


if __name__ == "__main__":
    main()
