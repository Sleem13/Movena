from rehabrl.clinical_protocols import CATALOG
from rehabrl.config import INJURY_TYPES


def test_clinical_protocol_catalog_integrity():
    assert len(CATALOG) == 26
    assert len({protocol.id for protocol in CATALOG}) == len(CATALOG)
    assert len({protocol.name for protocol in CATALOG}) == len(CATALOG)

    for protocol in CATALOG:
        assert protocol.summary
        assert protocol.outcome_measures
        assert protocol.red_flags
        assert protocol.precautions
        assert [phase.stage for phase in protocol.phases] == list(range(5))
        assert all(phase.goals for phase in protocol.phases)
        assert all(phase.interventions for phase in protocol.phases)
        assert all(phase.progression_criteria for phase in protocol.phases)
        assert all(url.startswith("https://") for _, url in protocol.sources)


def test_rl_protocol_mapping_exactly_matches_checkpoint_labels():
    mapped = [
        protocol.rl_injury_type
        for protocol in CATALOG
        if protocol.rl_injury_type is not None
    ]
    assert set(mapped) == set(INJURY_TYPES)
    assert len(mapped) == len(INJURY_TYPES) == 12
