"""Strict dataset boundary, independent of tensor and web frameworks."""
from __future__ import annotations
import json
import math
from pathlib import Path


def validate_manifest(document: dict, base: Path, require_files: bool = True) -> dict:
    if document.get('task') not in {'recognition', 'movement_quality'}:
        raise ValueError('Choose one explicit task: recognition or movement_quality')
    if document.get('coordinate_space') != 'world':
        raise ValueError('Training requires explicit world coordinates; image coordinates cannot be mixed silently')
    if not isinstance(document.get('pose_backbone_version'),str) or not document['pose_backbone_version'].strip():
        raise ValueError('Record the pose backbone version')
    visibility=document.get('min_anchor_visibility')
    if isinstance(visibility,bool) or not isinstance(visibility,(float,int)) or not math.isfinite(visibility) or not 0 < visibility <= 1:
        raise ValueError('Record a bounded min_anchor_visibility in the reviewed protocol')
    labels = document.get('labels', [])
    if len(labels) < 2 or len(labels) != len(set(labels)) or not all(isinstance(v, str) and v for v in labels):
        raise ValueError('At least two unique, non-empty class labels are required')
    samples = document.get('samples', [])
    if not samples:
        raise ValueError('No reviewed training samples are available')
    participants, identifiers, coverage = {}, set(), {s: set() for s in ['train', 'validation', 'holdout']}
    root = base.resolve()
    for sample in samples:
        for field in ['sample_id', 'participant_id', 'features', 'source', 'license_id']:
            if not isinstance(sample.get(field), str) or not sample[field].strip():
                raise ValueError(f'Missing {field}')
        if sample.get('reviewed') is not True:
            raise ValueError('Unreviewed samples cannot train or evaluate a candidate')
        identity = sample['sample_id']
        if identity in identifiers:
            raise ValueError('Duplicate sample identity')
        identifiers.add(identity)
        split = sample.get('split')
        if split not in coverage or sample.get('label') not in labels:
            raise ValueError('Unknown split or class label')
        participant = sample['participant_id']
        if participant in participants and participants[participant] != split:
            raise ValueError('Participant leakage across dataset splits')
        participants[participant] = split
        coverage[split].add(sample['label'])
        features = (root / sample['features']).resolve()
        if not features.is_relative_to(root) or features.suffix != '.npy':
            raise ValueError('Feature arrays must be .npy files inside the manifest directory')
        if require_files and not features.is_file():
            raise ValueError('Feature array is missing')
    if any(set(labels) != values for values in coverage.values()):
        raise ValueError('Each split must contain every class')
    return document


def load_manifest(path: Path) -> dict:
    return validate_manifest(json.loads(path.read_text(encoding='utf-8')), path.parent)
