def test_expansion_plan_keeps_planned_exercises_gated():
 text=open("docs/multi_exercise_app_expansion_plan.md",encoding="utf-8").read().lower();assert "`knee_extension`, and the rule-based `shoulder_abduction`" in text;assert "activation gate" in text and "feature delivery sequence" in text
