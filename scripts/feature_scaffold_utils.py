from pathlib import Path
import pandas as pd
BASE=["sample_id","dataset_name","exercise_id","participant_id","split","processing_status","raw_label","normalized_label","issue_label"]
def run_scaffold(unified_path:Path,output_path:Path,modalities:set[str],dry_run:bool):
    if not unified_path.exists():raise FileNotFoundError(f"Unified metadata not found: {unified_path}")
    data=pd.read_csv(unified_path);selected=data[data.modality.isin(modalities)].copy()
    if dry_run:return {"candidate_rows":len(selected),"output":str(output_path),"status":"dry_run"}
    out=pd.DataFrame({c:selected[c] if c in selected else None for c in BASE});out["processing_status"]="scaffold_pending_extraction";output_path.parent.mkdir(parents=True,exist_ok=True);out.to_csv(output_path,index=False);return {"candidate_rows":len(out),"output":str(output_path),"status":"written"}
