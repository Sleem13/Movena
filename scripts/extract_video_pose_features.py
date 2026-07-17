import argparse
from pathlib import Path
try:
 from scripts.feature_scaffold_utils import run_scaffold
except ModuleNotFoundError:
 from feature_scaffold_utils import run_scaffold
def main():
 p=argparse.ArgumentParser();p.add_argument("--input",type=Path,default=Path("data/processed/registry/unified_samples.csv"));p.add_argument("--output",type=Path,default=Path("data/processed/features/video_pose_features.csv"));p.add_argument("--dry-run",action="store_true");a=p.parse_args();print(run_scaffold(a.input,a.output,{"video","image"},a.dry_run));return 0
if __name__=="__main__":raise SystemExit(main())
