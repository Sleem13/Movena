from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_auto_routing_policy_requires_confirmation_and_blocks_unsupported_feedback():
    text = (ROOT / "docs" / "exercise_auto_routing_design.md").read_text(encoding="utf-8").lower()
    assert "0.80" in text and "0.50" in text
    assert "confirmation" in text
    assert "never provide" in text and "unsupported" in text
    assert "product thresholds" in text

