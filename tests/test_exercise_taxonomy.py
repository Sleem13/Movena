import pandas as pd
def test_taxonomy_supports_only_current_exercises():
 d=pd.read_csv("data/processed/registry/exercise_taxonomy.csv");supported=set(d[d.supported_in_app.astype(str).str.lower()=="true"].exercise_id)
 assert supported=={"bodyweight_squat","sit_to_stand","knee_extension","shoulder_abduction"};assert {"walking_gait_screen"}<=set(d.exercise_id)
