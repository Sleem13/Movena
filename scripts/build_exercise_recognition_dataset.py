"""Build a modality-separated dataset index for experimental exercise recognition."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

import pandas as pd


DEFAULT_INPUT = Path("data/processed/registry/unified_samples.csv")
DEFAULT_TAXONOMY = Path("data/processed/registry/exercise_taxonomy.csv")
DEFAULT_COVERAGE = Path("reports/dataset_audit/exercise_coverage_matrix.csv")
DEFAULT_OUTPUT_DIR = Path("data/processed/recognition")
DEFAULT_REPORT = Path("reports/model_reliability/exercise_recognition_dataset_report.md")
OUTPUT_COLUMNS = [
    "sample_id", "dataset_name", "file_path", "modality", "exercise_id", "raw_label",
    "normalized_label", "participant_id", "split", "label_quality", "requires_manual_review",
    "training_ready", "reason_excluded", "recognition_track",
]
TRACK_BY_MODALITY = {
    "video": "video_pose_recognition",
    "skeleton_2d": "skeleton_sequence_recognition",
    "skeleton_3d": "skeleton_sequence_recognition",
    "sensor_timeseries": "sensor_timeseries_recognition",
    "image": "image_pose_recognition",
    "tabular_features": "tabular_feature_recognition",
}


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def build_recognition_dataset(
    unified_samples_path: Path,
    taxonomy_path: Path,
    output_path: Path,
    report_path: Path,
    *,
    coverage_path: Path | None = None,
    include_low_confidence: bool = False,
    min_samples_per_class: int = 5,
    dry_run: bool = False,
) -> pd.DataFrame:
    samples = pd.read_csv(unified_samples_path)
    taxonomy = pd.read_csv(taxonomy_path)
    known_taxonomy = set(taxonomy["exercise_id"].astype(str))
    coverage_available = bool(coverage_path and coverage_path.exists())

    rows: list[dict[str, object]] = []
    for sample in samples.to_dict("records"):
        exercise = str(sample.get("exercise_id", "unknown"))
        quality = str(sample.get("label_quality", "unknown")).lower()
        modality = str(sample.get("modality", "unknown"))
        track = TRACK_BY_MODALITY.get(modality, "unsupported")
        reasons: list[str] = []
        if exercise == "unknown" or exercise not in known_taxonomy:
            reasons.append("unknown_exercise_id")
        if quality == "low" and not include_low_confidence:
            reasons.append("low_confidence_label")
        if _truthy(sample.get("requires_manual_review", False)):
            reasons.append("manual_review_required")
        if str(sample.get("processing_status", "unknown")) != "ready":
            reasons.append("processing_not_ready")
        if track == "unsupported":
            reasons.append("unsupported_modality")
        rows.append({
            "sample_id": sample.get("sample_id"),
            "dataset_name": sample.get("dataset_name"),
            "file_path": sample.get("file_path"),
            "modality": modality,
            "exercise_id": exercise,
            "raw_label": sample.get("raw_label"),
            "normalized_label": sample.get("normalized_label"),
            "participant_id": sample.get("participant_id"),
            "split": sample.get("split", "unassigned"),
            "label_quality": quality,
            "requires_manual_review": _truthy(sample.get("requires_manual_review", False)),
            "training_ready": not reasons,
            "reason_excluded": ";".join(reasons),
            "recognition_track": track,
        })

    result = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    eligible = result[result["training_ready"]] if not result.empty else result
    class_counts = Counter(zip(eligible["recognition_track"], eligible["exercise_id"]))
    for index, row in result[result["training_ready"]].iterrows():
        count = class_counts[(row["recognition_track"], row["exercise_id"])]
        if count < min_samples_per_class:
            result.at[index, "training_ready"] = False
            result.at[index, "reason_excluded"] = f"insufficient_class_samples:{count}<{min_samples_per_class}"

    ready_count = int(result["training_ready"].sum()) if not result.empty else 0
    report = (
        "# Exercise Recognition Dataset Report\n\n"
        "This is an experimental, modality-separated recognition index. It does not activate analyzers or permit automatic routing.\n\n"
        f"- Total samples: {len(result)}\n"
        f"- Training-ready discovery samples: {ready_count}\n"
        f"- Excluded samples: {len(result) - ready_count}\n"
        f"- Include low-confidence labels: {include_low_confidence}\n"
        f"- Minimum samples per class/track: {min_samples_per_class}\n"
        f"- Coverage matrix available: {coverage_available}\n"
        f"- Samples by track: {result.recognition_track.value_counts().to_dict() if len(result) else {}}\n"
        f"- Ready samples by exercise: {result[result.training_ready].exercise_id.value_counts().to_dict() if len(result) else {}}\n\n"
        "Manual exercise selection remains primary. Unsupported exercise labels cannot produce movement feedback.\n"
    )
    if not dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result.to_csv(output_path, index=False)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--taxonomy", type=Path, default=DEFAULT_TAXONOMY)
    parser.add_argument("--coverage", type=Path, default=DEFAULT_COVERAGE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--include-low-confidence", action="store_true")
    parser.add_argument("--min-samples-per-class", type=int, default=5)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    output = args.output_dir / "exercise_recognition_samples.csv"
    result = build_recognition_dataset(
        args.input, args.taxonomy, output, args.report, coverage_path=args.coverage,
        include_low_confidence=args.include_low_confidence,
        min_samples_per_class=args.min_samples_per_class, dry_run=args.dry_run,
    )
    ready = int(result.training_ready.sum()) if len(result) else 0
    print(f"Recognition samples: {len(result)}; training-ready: {ready}; dry_run={args.dry_run}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

