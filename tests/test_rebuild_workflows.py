"""Run fixture routes in a subprocess so legacy test settings stay untouched."""
import subprocess
import sys
from pathlib import Path


def test_recovery_workflow_contracts_in_isolated_process():
    root = Path(__file__).resolve().parents[1]
    completed = subprocess.run([sys.executable, str(root / 'scripts/rebuild_workflow_smoke.py')],
                               cwd=root, capture_output=True, text=True, timeout=60)
    assert completed.returncode == 0, completed.stderr
