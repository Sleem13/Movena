from pathlib import Path

import pandas as pd

from scripts.create_participant_metadata_template import create_participant_metadata_template


def test_participant_metadata_template_creates_and_preserves_rows(tmp_path: Path):
    annotations = tmp_path / "annotations.csv"
    output = tmp_path / "participants.csv"
    pd.DataFrame({"participant_id": ["P001", "P002", "", "P001"]}).to_csv(annotations, index=False)
    pd.DataFrame([{
        "participant_id": "P001", "age_group": "adult", "sex": "unknown",
        "clinical_group": "healthy", "experience_level": "beginner", "notes": "reviewed",
    }]).to_csv(output, index=False)

    result, added, preserved = create_participant_metadata_template(annotations, output)

    assert added == 1 and preserved == 1
    assert set(result["participant_id"]) == {"P001", "P002"}
    assert result.set_index("participant_id").loc["P001", "age_group"] == "adult"
    assert result.set_index("participant_id").loc["P002", "age_group"] == "unknown"
