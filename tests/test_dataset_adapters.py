import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.datasets.adapters import CustomVideosAdapter, GenericDatasetAdapter, SquatKaggleAdapter, ZenodoSquatAdapter


def test_initial_adapters_are_conservative(tmp_path):
    custom = tmp_path / "custom"
    (custom / "squat_correct").mkdir(parents=True)
    (custom / "squat_correct" / "a.mp4").write_bytes(b"video")
    assert CustomVideosAdapter(custom).is_compatible_with_current_pipeline() is True
    assert CustomVideosAdapter(custom).normalize_labels("squat_correct") == ("bodyweight_squat", "squat_correct")

    kaggle = tmp_path / "kaggle"
    kaggle.mkdir()
    (kaggle / "labels.csv").write_text("label\n", encoding="utf-8")
    assert SquatKaggleAdapter(kaggle).is_compatible_with_current_pipeline() is False
    assert GenericDatasetAdapter(kaggle).is_compatible_with_current_pipeline() is False
    assert ZenodoSquatAdapter(tmp_path / "missing").is_available() is False

