"""Measure Zenodo train/test drift and build a reproducible visual error sample."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import pandas as pd
from scipy.stats import ks_2samp

try:
    from .train_zenodo_squat_baseline import (
        DEFAULT_FEATURES,
        DEFAULT_METADATA,
        NON_FEATURE_COLUMNS,
        prepare_training_table,
        resolve_image_path,
    )
except ImportError:
    from train_zenodo_squat_baseline import (
        DEFAULT_FEATURES,
        DEFAULT_METADATA,
        NON_FEATURE_COLUMNS,
        prepare_training_table,
        resolve_image_path,
    )


DEFAULT_PREDICTIONS = Path("reports/model_reliability/zenodo_posture_holdout_predictions.csv")
DEFAULT_DRIFT_CSV = Path("reports/model_reliability/zenodo_posture_feature_drift.csv")
DEFAULT_REPORT = Path("reports/model_reliability/zenodo_posture_distribution_shift.md")
DEFAULT_REVIEW_MANIFEST = Path("reports/model_reliability/zenodo_posture_visual_review_manifest.csv")
DEFAULT_CONTACT_SHEET = Path("reports/model_reliability/zenodo_posture_error_contact_sheet.jpg")
DRIFT_COLUMNS = [
    "scope",
    "feature",
    "train_rows",
    "test_rows",
    "train_mean",
    "test_mean",
    "standardized_mean_difference",
    "ks_statistic",
    "ks_pvalue",
]


def standardized_mean_difference(train: pd.Series, test: pd.Series) -> float:
    pooled_variance = (float(train.var(ddof=1)) + float(test.var(ddof=1))) / 2
    if not math.isfinite(pooled_variance) or pooled_variance <= 0:
        return 0.0
    return float((test.mean() - train.mean()) / math.sqrt(pooled_variance))


def drift_rows(table: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    scopes = [("overall", table)] + [
        (f"label:{label}", table[table["label"].eq(label)])
        for label in sorted(table["label"].unique())
    ]
    for scope, scoped in scopes:
        train = scoped[scoped["source_split"].eq("train")]
        test = scoped[scoped["source_split"].eq("test")]
        for feature in features:
            train_values = pd.to_numeric(train[feature], errors="coerce").dropna()
            test_values = pd.to_numeric(test[feature], errors="coerce").dropna()
            if train_values.empty or test_values.empty:
                continue
            ks = ks_2samp(train_values, test_values, method="auto")
            rows.append(
                {
                    "scope": scope,
                    "feature": feature,
                    "train_rows": int(len(train_values)),
                    "test_rows": int(len(test_values)),
                    "train_mean": float(train_values.mean()),
                    "test_mean": float(test_values.mean()),
                    "standardized_mean_difference": standardized_mean_difference(
                        train_values, test_values
                    ),
                    "ks_statistic": float(ks.statistic),
                    "ks_pvalue": float(ks.pvalue),
                }
            )
    return pd.DataFrame(rows, columns=DRIFT_COLUMNS)


def detection_coverage(metadata_path: Path, detected_paths: set[str]) -> pd.DataFrame:
    metadata = pd.read_csv(metadata_path, dtype=str).fillna("")
    if "source_split" not in metadata:
        raise ValueError("Metadata must include source_split; regenerate it first.")
    metadata["detected"] = metadata["image_path"].astype(str).isin(detected_paths)
    coverage = (
        metadata.groupby(["source_split", "label"], dropna=False)["detected"]
        .agg(["count", "sum"])
        .reset_index()
        .rename(columns={"count": "prepared_images", "sum": "detected_images"})
    )
    coverage["missed_images"] = coverage["prepared_images"] - coverage["detected_images"]
    coverage["detection_rate"] = coverage["detected_images"] / coverage["prepared_images"]
    return coverage


def select_visual_review(predictions_path: Path, samples_per_pair: int) -> pd.DataFrame:
    predictions = pd.read_csv(predictions_path)
    required = {"image_path", "actual_label", "predicted_label", "confidence", "is_error", "error_pair"}
    if missing := required.difference(predictions.columns):
        raise ValueError("Prediction evidence is missing: " + ", ".join(sorted(missing)))
    is_error = predictions["is_error"].astype(str).str.lower().isin({"true", "1"})
    errors = predictions[is_error].copy()
    errors = errors.sort_values(
        ["error_pair", "confidence", "image_path"], ascending=[True, False, True]
    )
    selected = errors.groupby("error_pair", sort=True, group_keys=False).head(samples_per_pair)
    selected = selected.reset_index(drop=True)
    selected.insert(0, "review_id", [f"ZR-{index + 1:03d}" for index in range(len(selected))])
    selected["review_status"] = "pending_human_review"
    selected["review_notes"] = ""
    return selected


def create_contact_sheet(review: pd.DataFrame, output_path: Path) -> Path:
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageOps
    except ImportError as exc:
        raise RuntimeError("Pillow is required to create the visual review contact sheet.") from exc
    if review.empty:
        raise ValueError("Cannot create a contact sheet without review rows.")
    columns = 3
    tile_width, image_height, text_height = 360, 250, 72
    tile_height = image_height + text_height
    rows = math.ceil(len(review) / columns)
    sheet = Image.new("RGB", (columns * tile_width, rows * tile_height), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for position, row in enumerate(review.itertuples(index=False)):
        image_path = resolve_image_path(str(row.image_path))
        with Image.open(image_path) as source:
            source = ImageOps.exif_transpose(source).convert("RGB")
            thumbnail = ImageOps.contain(source, (tile_width - 12, image_height - 12))
        x = (position % columns) * tile_width
        y = (position // columns) * tile_height
        paste_x = x + (tile_width - thumbnail.width) // 2
        paste_y = y + (image_height - thumbnail.height) // 2
        sheet.paste(thumbnail, (paste_x, paste_y))
        draw.rectangle((x, y, x + tile_width - 1, y + tile_height - 1), outline="#cbd5e1")
        draw.text(
            (x + 8, y + image_height + 6),
            f"{row.review_id}  {row.actual_label} -> {row.predicted_label}",
            fill="#0f172a",
            font=font,
        )
        draw.text(
            (x + 8, y + image_height + 28),
            f"confidence={float(row.confidence):.3f}  {Path(str(row.image_path)).name}",
            fill="#334155",
            font=font,
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, quality=90)
    return output_path


def analyze_distribution_shift(
    features_path: Path,
    metadata_path: Path,
    predictions_path: Path,
    drift_csv: Path,
    report_path: Path,
    review_manifest: Path,
    contact_sheet: Path | None,
    samples_per_pair: int = 6,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    table, leakage_audit = prepare_training_table(features_path, metadata_path)
    features = [
        column
        for column in table.columns
        if column not in NON_FEATURE_COLUMNS and pd.api.types.is_numeric_dtype(table[column])
    ]
    drift = drift_rows(table, features)
    drift_csv.parent.mkdir(parents=True, exist_ok=True)
    drift.to_csv(drift_csv, index=False)
    coverage = detection_coverage(metadata_path, set(table["image_path"].astype(str)))
    review = select_visual_review(predictions_path, samples_per_pair)
    review_manifest.parent.mkdir(parents=True, exist_ok=True)
    review.to_csv(review_manifest, index=False)
    if contact_sheet is not None:
        create_contact_sheet(review, contact_sheet)

    top_overall = (
        drift[drift["scope"].eq("overall")]
        .assign(abs_smd=lambda frame: frame["standardized_mean_difference"].abs())
        .sort_values(["ks_statistic", "abs_smd"], ascending=False)
        .head(5)
    )
    summary = {
        "prepared_images": int(coverage["prepared_images"].sum()),
        "detected_images": int(coverage["detected_images"].sum()),
        "detection_rate": float(coverage["detected_images"].sum() / coverage["prepared_images"].sum()),
        "feature_scope_rows": int(len(drift)),
        "visual_review_rows": int(len(review)),
        "participant_grouped_holdout": bool(leakage_audit["participant_grouped_holdout"]),
        "promotion_supported": False,
    }
    coverage_lines = [
        f"| {row.source_split} | {row.label} | {row.prepared_images} | {row.detected_images} | {row.missed_images} | {row.detection_rate:.3f} |"
        for row in coverage.itertuples(index=False)
    ]
    drift_lines = [
        f"| `{row.feature}` | {row.train_mean:.3f} | {row.test_mean:.3f} | {row.standardized_mean_difference:.3f} | {row.ks_statistic:.3f} | {row.ks_pvalue:.2e} |"
        for row in top_overall.itertuples(index=False)
    ]
    report = [
        "# Zenodo Posture Distribution-Shift Review",
        "",
        "## Scope",
        "",
        "This report compares publisher train/test feature distributions among pose-detected images and separately audits pose-detection coverage. It does not establish participant independence or clinical validity.",
        "",
        f"- Prepared images: {summary['prepared_images']}",
        f"- Pose-detected images: {summary['detected_images']}",
        f"- Detection rate: {summary['detection_rate']:.3f}",
        f"- Visual-review sample: {summary['visual_review_rows']} high-confidence errors",
        "",
        "## Pose Detection Coverage",
        "",
        "| Split | Label | Prepared | Detected | Missed | Detection rate |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
        *coverage_lines,
        "",
        "## Largest Overall Feature Shifts",
        "",
        "| Feature | Train mean | Test mean | Standardized difference | KS statistic | KS p-value |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
        *drift_lines,
        "",
        "The complete overall and class-conditional results are stored in the drift CSV. Statistical significance is descriptive because images may not be participant-independent.",
        "",
        "## Visual Review Protocol",
        "",
        "The manifest selects the highest-confidence errors within every observed confusion pair. Reviewers should record framing, viewpoint, occlusion, source-label ambiguity, pose-landmark plausibility, and whether static geometry supports the source label. The sample must not be used to tune against the test set.",
        "",
        "Manual observations for the generated contact sheet are recorded in `zenodo_posture_visual_review.md` and kept separate from this reproducible statistical report.",
        "",
        "## Decision",
        "",
        "Promotion remains unsupported. Distribution shift, source-label ambiguity, and participant identity must be resolved using development data or a new participant-grouped dataset; the source test set remains audit-only.",
        "",
    ]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report), encoding="utf-8")
    return drift, review, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, default=DEFAULT_FEATURES)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--predictions", type=Path, default=DEFAULT_PREDICTIONS)
    parser.add_argument("--drift-csv", type=Path, default=DEFAULT_DRIFT_CSV)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--review-manifest", type=Path, default=DEFAULT_REVIEW_MANIFEST)
    parser.add_argument("--contact-sheet", type=Path, default=DEFAULT_CONTACT_SHEET)
    parser.add_argument("--samples-per-pair", type=int, default=6)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        _, _, summary = analyze_distribution_shift(
            args.features,
            args.metadata,
            args.predictions,
            args.drift_csv,
            args.report,
            args.review_manifest,
            args.contact_sheet,
            args.samples_per_pair,
        )
    except Exception as exc:
        print(f"Zenodo distribution-shift analysis failed: {exc}", file=sys.stderr)
        return 1
    print(
        f"Audited {summary['detected_images']} detected images; "
        f"visual-review rows: {summary['visual_review_rows']}"
    )
    print(f"Report: {args.report}")
    print(f"Contact sheet: {args.contact_sheet}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
