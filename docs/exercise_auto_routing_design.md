# Future Exercise Auto-Routing Design

Automatic routing is not enabled. The intended confirmation-first flow is:

1. A recognition model predicts an exercise distribution.
2. At confidence **>= 0.80**, show a strong suggestion only when an analyzer exists, then ask for confirmation.
3. At confidence **0.50 to 0.79**, show a weak suggestion and require manual selection.
4. At confidence **< 0.50**, require manual selection without a routing suggestion.
5. If the predicted exercise has no supported analyzer, state that it is planned and not currently supported.
6. Never provide biomechanics feedback for an unsupported exercise.

These are product thresholds, not clinical thresholds. They do not establish safety, diagnostic accuracy, or treatment suitability.

Any future trial requires a model card, participant-grouped holdout evaluation, minimum per-class recall, confidence calibration, systematic-routing error analysis, explicit confirmation, audit logging, and rollback. Recognition alone must never invoke an analyzer. Manual selection remains primary.

