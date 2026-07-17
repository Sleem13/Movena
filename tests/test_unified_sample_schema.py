import json
def test_unified_schema_is_valid_json_and_has_core_fields():
 d=json.load(open("data/processed/registry/unified_sample_schema.json",encoding="utf-8"));assert d["type"]=="object";assert {"sample_id","modality","exercise_id","requires_manual_review"}<=set(d["properties"])
