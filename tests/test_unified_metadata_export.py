import pandas as pd
from scripts.export_unified_dataset_metadata import export_unified_metadata
def test_export_preserves_unknown_label(tmp_path):
 root=tmp_path/"raw"/"mystery";root.mkdir(parents=True);(root/"sample.csv").write_text("a,b\n1,2")
 registry=tmp_path/"registry.csv";pd.DataFrame([{"dataset_name":"mystery","source_path":str(root),"status":"needs_manual_mapping","primary_modality":"tabular_features","requires_manual_label_mapping":True}]).to_csv(registry,index=False)
 out=export_unified_metadata(registry,tmp_path/"samples.csv",tmp_path/"summary.md")
 assert len(out)==1 and out.iloc[0].exercise_id=="unknown" and bool(out.iloc[0].requires_manual_review)
