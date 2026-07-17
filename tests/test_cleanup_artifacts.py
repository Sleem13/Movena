import os
from pathlib import Path

from scripts.cleanup_artifacts import cleanup_artifacts


def make_old(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"artifact")
    os.utime(path, (1, 1))


def test_cleanup_dry_run_does_not_delete(tmp_path):
    artifact = tmp_path / "overlays" / "old.mp4"
    make_old(artifact)
    result = cleanup_artifacts(tmp_path, 1, dry_run=True, now=10_000)
    assert result == {"deleted_files": 1, "freed_bytes": 8}
    assert artifact.exists()


def test_cleanup_deletes_only_artifact_subdirectories(tmp_path):
    artifact = tmp_path / "reports" / "old.pdf"
    outside = tmp_path / "source.py"
    make_old(artifact)
    make_old(outside)
    result = cleanup_artifacts(tmp_path, 1, now=10_000)
    assert result["deleted_files"] == 1
    assert not artifact.exists()
    assert outside.exists()
