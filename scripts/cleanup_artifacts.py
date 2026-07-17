"""Safely remove expired temporary report and overlay artifacts."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.core.config import get_settings


def cleanup_artifacts(
    artifact_root: Path,
    retention_hours: float,
    *,
    dry_run: bool = False,
    now: float | None = None,
) -> dict[str, int]:
    root = artifact_root.resolve()
    cutoff = (time.time() if now is None else now) - retention_hours * 3600
    files = bytes_freed = 0
    for folder_name in ("overlays", "reports"):
        folder = root / folder_name
        if not folder.exists():
            continue
        for candidate in folder.rglob("*"):
            if candidate.is_symlink() or not candidate.is_file():
                continue
            resolved = candidate.resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                continue
            stat = resolved.stat()
            if stat.st_mtime >= cutoff:
                continue
            files += 1
            bytes_freed += stat.st_size
            if not dry_run:
                resolved.unlink()
    return {"deleted_files": files, "freed_bytes": bytes_freed}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Report without deleting files.")
    parser.add_argument("--retention-hours", type=float, default=None)
    args = parser.parse_args()

    settings = get_settings()
    retention = settings.artifact_retention_hours if args.retention_hours is None else args.retention_hours
    summary = cleanup_artifacts(settings.artifact_dir, retention, dry_run=args.dry_run)
    action = "Would delete" if args.dry_run else "Deleted"
    print(f"{action} {summary['deleted_files']} artifact(s); {summary['freed_bytes']} byte(s) freed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
