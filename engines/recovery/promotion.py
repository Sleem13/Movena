"""Reject promotion when evidence is missing, incomparable or regresses."""
from __future__ import annotations
import math

HIGHER_IS_BETTER = {'recognition_macro_f1', 'quality_macro_f1', 'rejection_recall'}
LOWER_IS_BETTER = {'rep_count_mae', 'latency_p95_ms', 'peak_memory_mb'}
REQUIRED_METRICS = HIGHER_IS_BETTER | LOWER_IS_BETTER


def promotion_decision(baseline: dict, candidate: dict, *, required_tasks: tuple[str, ...] = ()) -> dict:
    """The caller supplies the reviewed task inventory, never a candidate's list.

    Aggregate improvements cannot hide a regression on a supported task.
    This validates evidence structure; it does not itself run evaluation.
    """
    reasons = []
    if not required_tasks or len(set(required_tasks)) != len(required_tasks):
        reasons.append('A nonempty reviewed task inventory is required')
    for label, report in [('baseline', baseline), ('candidate', candidate)]:
        if not report.get('dataset_digest') or report.get('evaluated_videos', 0) <= 0:
            reasons.append(f'{label}: missing evaluated holdout evidence')
        if report.get('participant_separated') is not True or report.get('labels_reviewed') is not True:
            reasons.append(f'{label}: labels/splits are not reviewed')
        if not report.get('engine_version'):
            reasons.append(f'{label}: missing engine version')
        for metric in REQUIRED_METRICS:
            value = report.get('metrics', {}).get(metric)
            if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or value < 0:
                reasons.append(f'{label}: missing or invalid {metric}')
            elif metric in HIGHER_IS_BETTER and value > 1:
                reasons.append(f'{label}: {metric} must be between zero and one')
    for field in ['dataset_digest', 'protocol_version', 'hardware_id']:
        if not baseline.get(field) or baseline.get(field) != candidate.get(field):
            reasons.append(f'Benchmarks differ or omit {field}')
    if baseline.get('evaluated_videos') != candidate.get('evaluated_videos'):
        reasons.append('Benchmarks evaluated different video counts')
    if candidate.get('reviewer_approved') is not True:
        reasons.append('Candidate benchmark has not been reviewed')
    if candidate.get('unsafe_acceptances', -1) != 0:
        reasons.append('Safety regression suite must have zero unsafe acceptances')
    for label, report in [('baseline', baseline), ('candidate', candidate)]:
        tasks = report.get('tasks', {})
        if set(tasks) != set(required_tasks):
            reasons.append(f'{label}: supported task coverage differs from the reviewed inventory')
        for task in required_tasks:
            evidence = tasks.get(task, {})
            count = evidence.get('evaluated_videos')
            if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
                reasons.append(f'{label}: {task} has no evaluated evidence')
            if evidence.get('unsafe_acceptances', -1) != 0:
                reasons.append(f'{label}: {task} has missing or failing rejection evidence')
            for metric in REQUIRED_METRICS:
                value = evidence.get('metrics', {}).get(metric)
                if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or value < 0 or (metric in HIGHER_IS_BETTER and value > 1):
                    reasons.append(f'{label}: {task} has missing or invalid {metric}')
    if not reasons:
        for task in required_tasks:
            previous, current = baseline['tasks'][task], candidate['tasks'][task]
            if previous['evaluated_videos'] != current['evaluated_videos'] or not previous.get('dataset_digest') or previous.get('dataset_digest') != current.get('dataset_digest'):
                reasons.append(f'{task}: task holdout samples differ or are unspecified')
            for metric in REQUIRED_METRICS:
                old, new = previous['metrics'][metric], current['metrics'][metric]
                if (metric in HIGHER_IS_BETTER and new < old) or (metric in LOWER_IS_BETTER and new > old):
                    reasons.append(f'{task}: regression in {metric}')
    if not reasons:
        for metric in HIGHER_IS_BETTER:
            if candidate['metrics'][metric] < baseline['metrics'][metric]:
                reasons.append(f'Regression: {metric}')
        for metric in LOWER_IS_BETTER:
            if candidate['metrics'][metric] > baseline['metrics'][metric]:
                reasons.append(f'Regression: {metric}')
    return {'promotable': not reasons, 'reasons': reasons, 'clinical_validation': False}
