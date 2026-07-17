def test_expansion_plan_keeps_planned_exercises_gated():
 text=open("docs/multi_exercise_app_expansion_plan.md",encoding="utf-8").read().lower();assert "`shoulder_abduction`, and the rule-based `hip_abduction`" in text;assert "activation gate" in text and "feature delivery sequence" in text
