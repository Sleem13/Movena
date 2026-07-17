"""Export adapter-normalized discovery metadata without declaring training readiness."""
from __future__ import annotations
import argparse,sys
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"backend"))
from app.datasets.registry import create_adapter
from app.datasets.adapters.generic_dataset_adapter import GenericDatasetAdapter

SCHEMA_COLUMNS=["sample_id","dataset_name","source_path","file_path","modality","exercise_id","raw_label","normalized_label","issue_label","participant_id","session_id","view_type","recording_quality","duration_sec","fps","frame_count","has_manual_rep_count","expected_reps","split","is_augmented","adapter_name","processing_status","requires_manual_review","notes"]
def export_unified_metadata(registry_path,output_path,summary_path):
    registry=pd.read_csv(registry_path);rows=[];skipped=[]
    for item in registry.to_dict("records"):
        if item["status"]=="missing_or_incomplete":skipped.append(item["dataset_name"]);continue
        path=ROOT/str(item["source_path"]);adapter=create_adapter(item["dataset_name"],path)
        if type(adapter).__name__=="GenericDatasetAdapter":adapter.modality=item["primary_modality"]
        for sample in adapter.export_unified_metadata():
            sample["modality"]=item["primary_modality"];sample["requires_manual_review"]=bool(sample["requires_manual_review"] or item["requires_manual_label_mapping"]);rows.append(sample)
    out=pd.DataFrame(rows,columns=SCHEMA_COLUMNS);output_path.parent.mkdir(parents=True,exist_ok=True);out.to_csv(output_path,index=False)
    counts=out.modality.value_counts().to_dict() if len(out) else {}
    summary_path.parent.mkdir(parents=True,exist_ok=True);summary_path.write_text("# Unified Metadata Export Summary\n\n"+f"- Samples discovered: {len(out)}\n- Missing/incomplete datasets skipped: {', '.join(skipped) or 'None'}\n- Modalities: {counts}\n\nUnknown labels remain unknown and require review. This is discovery metadata, not a training-ready table.\n",encoding="utf-8");return out
def main():
    p=argparse.ArgumentParser();p.add_argument("--registry",type=Path,default=Path("data/processed/registry/dataset_registry.csv"));p.add_argument("--output",type=Path,default=Path("data/processed/registry/unified_samples.csv"));p.add_argument("--summary",type=Path,default=Path("reports/dataset_audit/unified_metadata_export_summary.md"));a=p.parse_args();d=export_unified_metadata(a.registry,a.output,a.summary);print(f"Exported {len(d)} sample metadata rows to {a.output}");return 0
if __name__=="__main__":raise SystemExit(main())
