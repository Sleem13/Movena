# Roadmap Decision Log

1. **Mobile is Sprint 16, not the immediate next sprint.** Mobile would amplify unstable identity, data, and API assumptions, so it follows the foundations that make capture, history, and results governable.
2. **Auth, roles, and privacy come before mobile.** Patient and therapist resources require identity, authorization, consent placeholders, retention/deletion rules, and audit foundations before remote access.
3. **Multi-dataset ML/DL architecture precedes serious model expansion.** Modality, taxonomy, schemas, evaluation boundaries, model registry, and model cards must exist before experiments can be compared safely.
4. **Dataset adapters precede use of all datasets.** Sources differ in modality, labels, participants, coordinates, licensing, quality, and protocols. Adapters prevent leakage and invalid merging.
5. **Cloud deployment waits for API/auth/privacy foundations.** Internet exposure without access control, secure persistence, consent, monitoring, and incident procedures creates unnecessary risk.
6. **Rule-based analyzers remain primary.** Their validity, thresholds, score components, and feedback are inspectable and controllable for the current evidence base.
7. **ML/DL remains experimental until promotion gates pass.** Promotion requires representative real data, complete annotations, participant-grouped holdout, acceptable metrics, error analysis, a model card, safety review, and rollback.
8. **Unsupported exercises are planned only.** A dataset label or UI concept is not an analyzer; dedicated validity, phases, scoring, confidence, safety, and validation are required.

Product release, model promotion, and clinical research validation remain distinct approvals.

9. **Training tracks remain separate.** Video pose features, skeleton sequences, sensors, and static images have different semantics and validation requirements; fusion is research-only.
