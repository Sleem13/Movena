import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analyze_zenodo_model_errors import analyze_errors
from predict_zenodo_squat_baseline import predict_rows
from test_train_zenodo_squat_baseline import write_training_files
from train_zenodo_squat_baseline import train_zenodo_baselines


def test_offline_prediction_returns_probabilities_and_research_scope(tmp_path):
    features, metadata = write_training_files(tmp_path)
    model_dir = tmp_path / "model"
    train_zenodo_baselines(features, metadata, model_dir)
    selected_image = str(tmp_path / "test" / "good" / "0.jpg")

    prediction = predict_rows(
        model_dir / "artifacts" / "zenodo_squat_posture_baseline.pkl",
        features,
        selected_image,
    )[0]

    assert prediction["image_path"] == selected_image
    assert prediction["predicted_label"] in {"good", "bad_back", "bad_heel"}
    assert 0 <= prediction["confidence"] <= 1
    assert set(prediction["class_probabilities"]) == {"good", "bad_back", "bad_heel"}
    assert prediction["scope"] == "static_squat_posture_research_only"


def test_error_analysis_exports_source_holdout_evidence(tmp_path):
    features, metadata = write_training_files(tmp_path)
    model_dir = tmp_path / "model"
    train_zenodo_baselines(features, metadata, model_dir)
    output_csv = tmp_path / "errors.csv"
    output_md = tmp_path / "errors.md"

    result, summary = analyze_errors(
        features,
        metadata,
        model_dir / "artifacts" / "zenodo_squat_posture_baseline.pkl",
        output_csv,
        output_md,
    )

    assert len(result) == 9
    assert summary["evaluated_rows"] == 9
    assert summary["correct_rows"] + summary["error_rows"] == 9
    assert summary["participant_grouped_holdout"] is False
    assert summary["promotion_supported"] is False
    assert set(summary["selective_performance"]) == {
        "at_least_0.50", "at_least_0.75", "at_least_0.90", "at_least_0.95"
    }
    assert output_csv.exists()
    report = output_md.read_text(encoding="utf-8")
    assert "Confusion Matrix" in report
    assert "Promotion is not supported" in report
