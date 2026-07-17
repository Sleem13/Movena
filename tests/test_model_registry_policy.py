from app.ml.model_registry import promotion_eligible
def test_registry_refuses_unvalidated_promotion():
 ok,reasons=promotion_eligible({"status":"experimental","manual_annotations_used":False,"participant_grouped_holdout":False});assert not ok and len(reasons)>=3
 ok,_=promotion_eligible({"status":"candidate","manual_annotations_used":True,"participant_grouped_holdout":True,"model_card_path":"card.md"});assert ok
