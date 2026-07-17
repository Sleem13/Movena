import pandas as pd
from scripts.train_ml_track import validate_feature_table
def test_dry_run_validates_small_grouped_table(tmp_path):
 path=tmp_path/"features.csv";pd.DataFrame({"exercise_id":["bodyweight_squat"]*4,"participant_id":["p1","p2","p3","p4"],"split":["train","train","validation","holdout"],"label":["correct","issue","correct","issue"]}).to_csv(path,index=False)
 result=validate_feature_table(path,"bodyweight_squat");assert result["valid"] and result["rows"]==4
