"""Build the conservative, modality-aware Movena dataset registry."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import pandas as pd

DEFAULT_INPUT=Path("reports/dataset_audit/dataset_file_inventory.csv");DEFAULT_OUTPUT=Path("data/processed/registry/dataset_registry.csv");DEFAULT_SUMMARY=Path("reports/dataset_audit/dataset_modality_summary.md")
HIGH={"custom_videos","squat_kaggle","zenodo_squat_dataset"};COMPLEX={"kimore","ui_prmd","uci_physical_therapy_exercises","dyntherapy","rehab24_6","Physical-therapy exercises"}
REGISTRY_COLUMNS=["dataset_name","source_path","status","primary_modality","secondary_modalities","file_count","video_count","image_count","csv_count","json_count","mat_count","npy_count","annotation_file_count","has_labels","label_source","known_exercises","likely_exercise_family","usable_for_video_pose_pipeline","usable_for_skeleton_pipeline","usable_for_sensor_pipeline","usable_for_image_pose_pipeline","usable_for_tabular_feature_pipeline","usable_for_current_app","usable_for_current_squat_mvp","requires_adapter","requires_manual_label_mapping","priority","risks_or_limitations","notes"]
def normalize_modality(value,name):
    value=str(value)
    if value in {"missing","missing_or_incomplete"}:return "missing_or_incomplete"
    if value=="skeleton_csv":return "skeleton_3d"
    return value if value in {"video","image","skeleton_2d","skeleton_3d","sensor_timeseries","tabular_features","mixed","unknown"} else "unknown"
def build_registry(inventory_path,output_path,summary_path):
    inv=pd.read_csv(inventory_path);rows=[]
    for r in inv.itertuples(index=False):
        name=str(r.dataset_name);files=int(r.total_file_count);mod=normalize_modality(r.likely_modality,name);missing=files==0 or name=="uco_physical_rehab" or mod=="missing_or_incomplete"
        try: annotations=json.loads(str(r.annotation_candidate_files));ann_count=len(annotations)
        except Exception: annotations=[];ann_count=0
        labels=bool(ann_count or name=="custom_videos");known="bodyweight_squat" if name in HIGH and labels else "unknown"
        manual=not labels or name in COMPLEX or known=="unknown";adapter=name in COMPLEX or mod in {"mixed","unknown","skeleton_2d","skeleton_3d","sensor_timeseries"}
        video=mod=="video" and int(r.video_count)>0;image=mod=="image" and int(r.image_count)>0;skeleton=mod in {"skeleton_2d","skeleton_3d"};sensor=mod=="sensor_timeseries";tabular=mod=="tabular_features"
        understood=labels and not manual;status="missing_or_incomplete" if missing else ("ready" if name=="custom_videos" else "needs_manual_mapping" if manual else "usable_with_adapter" if adapter else "research_only")
        risks="Do not train until modality, labels, participants, licensing, and split leakage are reviewed."
        current=bool(name=="custom_videos" and understood)
        rows.append(dict(dataset_name=name,source_path=r.dataset_path,status=status,primary_modality=mod,secondary_modalities="",file_count=files,video_count=int(r.video_count),image_count=int(r.image_count),csv_count=int(r.csv_count),json_count=int(r.json_count),mat_count=int(r.mat_count),npy_count=int(r.npy_count),annotation_file_count=ann_count,has_labels=labels,label_source="folder/metadata" if labels else "unknown",known_exercises=known,likely_exercise_family="lower_body" if known=="bodyweight_squat" else "unknown",usable_for_video_pose_pipeline=video,usable_for_skeleton_pipeline=skeleton,usable_for_sensor_pipeline=sensor,usable_for_image_pose_pipeline=image,usable_for_tabular_feature_pipeline=tabular,usable_for_current_app=current,usable_for_current_squat_mvp=current,requires_adapter=bool(not missing and adapter),requires_manual_label_mapping=bool(not missing and manual),priority="high" if name in HIGH else "medium" if name in COMPLEX else "low",risks_or_limitations=risks,notes=str(r.notes) if pd.notna(r.notes) else ""))
    out=pd.DataFrame(rows,columns=REGISTRY_COLUMNS);output_path.parent.mkdir(parents=True,exist_ok=True);out.to_csv(output_path,index=False)
    modality_csv=summary_path.with_suffix(".csv");modality_csv.parent.mkdir(parents=True,exist_ok=True);out.groupby(["primary_modality","status"],dropna=False).size().reset_index(name="dataset_count").to_csv(modality_csv,index=False)
    lines=["# Dataset Modality Summary","",f"- Datasets: {len(out)}",f"- Ready: {(out.status=='ready').sum()}",f"- Missing/incomplete: {(out.status=='missing_or_incomplete').sum()}","","| Dataset | Status | Modality | Labels | Adapter |","|---|---|---|---|---|"]+[f"| {x.dataset_name} | {x.status} | {x.primary_modality} | {x.has_labels} | {x.requires_adapter} |" for x in out.itertuples()]+["","Training-ready is not inferred from file presence. Unknown labels remain unknown."]
    summary_path.write_text("\n".join(lines),encoding="utf-8");return out
def main():
    p=argparse.ArgumentParser();p.add_argument("--input",type=Path,default=DEFAULT_INPUT);p.add_argument("--output",type=Path,default=DEFAULT_OUTPUT);p.add_argument("--summary",type=Path,default=DEFAULT_SUMMARY);a=p.parse_args();d=build_registry(a.input,a.output,a.summary);print(f"Registered {len(d)} datasets. Registry: {a.output}");return 0
if __name__=="__main__":raise SystemExit(main())
