import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from manifest import validate_manifest
from promotion import promotion_decision, REQUIRED_METRICS


def manifest():
    return {'task': 'recognition', 'coordinate_space':'world', 'pose_backbone_version':'synthetic-test-only', 'min_anchor_visibility':.8, 'labels': ['squat', 'sit'], 'samples': [
        {'sample_id': f'{split}-{label}', 'participant_id': f'participant-{split}', 'features': f'{split}-{label}.npy',
         'split': split, 'label': label, 'reviewed': True, 'source': 'synthetic-unit-test', 'license_id': 'test-only'}
        for split in ['train', 'validation', 'holdout'] for label in ['squat', 'sit']]}


def report():
    return {'dataset_digest': 'same-holdout', 'evaluated_videos': 20, 'participant_separated': True,
        'labels_reviewed': True, 'engine_version': 'test-only', 'protocol_version': 'one', 'hardware_id': 'same',
        'reviewer_approved': True, 'unsafe_acceptances': 0, 'metrics': {k: .8 for k in REQUIRED_METRICS},
        'tasks': {'squat': {'evaluated_videos': 20, 'dataset_digest': 'same-task-holdout',
                           'unsafe_acceptances': 0, 'metrics': {k: .8 for k in REQUIRED_METRICS}}}}


class DatasetBoundaryTests(unittest.TestCase):
    def test_coordinate_provenance_and_normalization_protocol_are_required(self):
        for field,value in [('coordinate_space','image'),('pose_backbone_version',''),('min_anchor_visibility',float('nan')),('min_anchor_visibility',True)]:
            data=manifest();data[field]=value
            with self.assertRaises(ValueError):validate_manifest(data,Path.cwd(),False)

    def test_participant_leakage_is_rejected(self):
        data = manifest(); data['samples'][2]['participant_id'] = data['samples'][0]['participant_id']
        with self.assertRaisesRegex(ValueError, 'leakage'):
            validate_manifest(data, Path.cwd(), False)

    def test_unreviewed_and_outside_features_are_rejected(self):
        for key, value in [('reviewed', False), ('features', '../secret.npy')]:
            data = manifest(); data['samples'][0][key] = value
            with self.assertRaises(ValueError): validate_manifest(data, Path.cwd(), False)

    def test_missing_class_and_empty_data_are_rejected(self):
        for samples in [[], manifest()['samples'][:-1]]:
            data = manifest(); data['samples'] = samples
            with self.assertRaises(ValueError): validate_manifest(data, Path.cwd(), False)

    def test_complete_disjoint_manifest_is_accepted(self):
        self.assertEqual(validate_manifest(manifest(), Path.cwd(), False)['task'], 'recognition')


class PromotionTests(unittest.TestCase):
    def test_empty_benchmark_never_passes(self):
        self.assertFalse(promotion_decision({}, {})['promotable'])

    def test_regression_or_missing_metric_never_passes(self):
        for value in [None, float('nan'), .7]:
            candidate = report(); candidate['metrics']['rejection_recall'] = value
            self.assertFalse(promotion_decision(report(), candidate, required_tasks=('squat',))['promotable'])

    def test_different_hardware_or_data_never_passes(self):
        for field in ['hardware_id', 'dataset_digest']:
            candidate = report(); candidate[field] = 'different'
            self.assertFalse(promotion_decision(report(), candidate, required_tasks=('squat',))['promotable'])

    def test_passing_gate_does_not_claim_clinical_validation(self):
        result = promotion_decision(report(), report(), required_tasks=('squat',))
        self.assertTrue(result['promotable']); self.assertFalse(result['clinical_validation'])

    def test_aggregate_improvement_cannot_hide_task_rejection_regression(self):
        candidate = report()
        candidate['metrics']['rejection_recall'] = .99
        candidate['tasks']['squat']['metrics']['rejection_recall'] = .7
        self.assertFalse(promotion_decision(report(), candidate, required_tasks=('squat',))['promotable'])

    def test_unreviewed_task_inventory_and_missing_task_never_pass(self):
        self.assertFalse(promotion_decision(report(), report())['promotable'])
        self.assertFalse(promotion_decision(report(), report(), required_tasks=('squat', 'knee_extension'))['promotable'])
