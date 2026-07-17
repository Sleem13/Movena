ALLOWED_STATUSES={"experimental","candidate","app_optional","deprecated"}
def promotion_eligible(record):
    reasons=[]
    if not record.get("manual_annotations_used"):reasons.append("manual annotations are required")
    if not record.get("participant_grouped_holdout"):reasons.append("participant-grouped holdout is required")
    if not record.get("model_card_path"):reasons.append("model card is required")
    if record.get("status") not in {"candidate","app_optional"}:reasons.append("model must complete candidate review")
    return not reasons,reasons
