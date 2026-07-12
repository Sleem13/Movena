import sys
from pathlib import Path

import cv2
import numpy as np
import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from augment_custom_squat_videos import augment_frame, write_augmented_video


def tiny_video(path: Path) -> None:
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), 10, (32, 32))
    assert writer.isOpened()
    for value in [20, 80, 140]:
        writer.write(np.full((32, 32, 3), value, dtype=np.uint8))
    writer.release()


def test_mild_frame_augmentations_preserve_shape():
    frame = np.full((24, 32, 3), 100, dtype=np.uint8)
    for name, parameters in [
        ("horizontal_flip", {}), ("brightness", {"beta": 10}),
        ("contrast", {"alpha": 1.1}), ("slight_rotation", {"degrees": 4}),
        ("slight_zoom", {"scale": 0.95}), ("gaussian_noise", {"sigma": 2}),
    ]:
        result = augment_frame(frame, name, parameters)
        assert result.shape == frame.shape
        assert result.dtype == np.uint8


def test_augmented_video_is_separate_and_source_is_unchanged(tmp_path):
    source = tmp_path / "source.mp4"
    output = tmp_path / "augmented.mp4"
    tiny_video(source)
    original_size = source.stat().st_size

    write_augmented_video(source, output, "brightness", {"beta": 10})

    assert source.exists() and source.stat().st_size == original_size
    assert output.exists() and output.stat().st_size > 0
    with pytest.raises(FileExistsError):
        write_augmented_video(source, output, "brightness", {"beta": 10})
    with pytest.raises(ValueError, match="must not overwrite"):
        write_augmented_video(source, source, "brightness", {"beta": 10}, overwrite=True)
