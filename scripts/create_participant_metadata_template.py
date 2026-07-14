"""Create or extend pseudonymous participant metadata from manual annotations."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


DEFAULT_ANNOTATIONS = Path("data/processed/labels/manual_rep_annotations.csv")
DEFAULT_OUTPUT = Path("data/processed/labels/participant_metadata.csv")
METADATA_COLUMNS = [
    "participant_id", "age_group", "sex", "clinical_group", "experience_level", "notes"
]


def create_participant_metadata_template(
    annotations_path: Path, output_path: Path
) -> tuple[pd.DataFrame, int, int]:
    if not annotations_path.exists():
        raise FileNotFoundError(f"Annotation file not found: {annotations_path}")
    annotations = pd.read_csv(annotations_path, dtype=str, keep_default_na=False)
    if "participant_id" not in annotations.columns:
        raise ValueError("Annotation file is missing: participant_id")
    participant_ids = sorted({
        value.strip() for value in annotations["participant_id"] if value.strip() and value.strip().lower() != "unknown"
    })

    existing: dict[str, dict[str, str]] = {}
    if output_path.exists() and output_path.stat().st_size:
        prior = pd.read_csv(output_path, dtype=str, keep_default_na=False)
        if "participant_id" not in prior.columns:
            raise ValueError("Existing participant metadata is missing: participant_id")
        for record in prior.to_dict("records"):
            key = str(record.get("participant_id", "")).strip()
            if key and key not in existing:
                existing[key] = {column: str(record.get(column, "")) for column in METADATA_COLUMNS}

    rows: list[dict[str, str]] = []
    added = preserved = 0
    for participant_id in participant_ids:
        if participant_id in existing:
            row = existing[participant_id].copy()
            preserved += 1
        else:
            row = {column: "unknown" for column in METADATA_COLUMNS}
            row.update({"participant_id": participant_id, "notes": ""})
            added += 1
        rows.append(row)
    # Preserve reviewed metadata even if an annotation row is temporarily removed.
    for participant_id, row in sorted(existing.items()):
        if participant_id not in participant_ids:
            rows.append(row)
            preserved += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result = pd.DataFrame(rows, columns=METADATA_COLUMNS)
    result.to_csv(output_path, index=False)
    return result, added, preserved


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", type=Path, default=DEFAULT_ANNOTATIONS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        data, added, preserved = create_participant_metadata_template(args.annotations, args.output)
    except Exception as exc:
        print(f"Participant metadata creation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Saved {len(data)} participants to {args.output}")
    print(f"Added participants: {added}; preserved participants: {preserved}")
    if data.empty:
        print("WARNING: No reviewed participant IDs are available yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
