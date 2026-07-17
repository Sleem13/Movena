"""Conservative classic-ML track orchestrator; never promotes models."""
import argparse,json
from datetime import datetime,timezone
from pathlib import Path
import pandas as pd
TRACKS={"video_pose","skeleton_sequence","sensor_timeseries","image_pose","tabular_feature"};MODELS={"random_forest","svc","logistic_regression"}
def validate_feature_table(path,exercise,allow_non_grouped=False):
    if not path.exists():return {"valid":False,"reasons":[f"feature table not found: {path}"],"rows":0}
    data=pd.read_csv(path);reasons=[]
    for c in ("exercise_id","participant_id","split"): 
        if c not in data:reasons.append(f"missing column: {c}")
    labels=[c for c in ("normalized_label","issue_label","label") if c in data]
    if not labels:reasons.append("missing label column")
    else:
        values=data[labels[0]].dropna().astype(str);values=values[~values.isin(["unknown",""])]
        if values.nunique()<2:reasons.append("at least two known label classes are required")
    if not allow_non_grouped and ("participant_id" not in data or data.participant_id.isna().any() or "split" not in data):reasons.append("participant-grouped split is required")
    return {"valid":not reasons,"reasons":reasons,"rows":len(data)}
def main():
 p=argparse.ArgumentParser();p.add_argument("--track",choices=sorted(TRACKS),required=True);p.add_argument("--exercise",default="all_supported");p.add_argument("--features-path",type=Path);p.add_argument("--output-dir",type=Path,default=Path("models/track_runs"));p.add_argument("--model",choices=sorted(MODELS),default="random_forest");p.add_argument("--dry-run",action="store_true");p.add_argument("--allow-non-grouped",action="store_true");a=p.parse_args();path=a.features_path or Path(f"data/processed/features/{a.track}_features.csv");result=validate_feature_table(path,a.exercise,a.allow_non_grouped);result.update(track=a.track,exercise=a.exercise,model=a.model,dry_run=a.dry_run,automatic_promotion=False);print(json.dumps(result,indent=2));
 if a.dry_run:return 0
 if not result["valid"]:return 2
 print("Training implementation is intentionally deferred; existing v2 scripts remain authoritative.");return 2
if __name__=="__main__":raise SystemExit(main())
