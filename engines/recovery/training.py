"""CPU-capable candidate training. Holdout data is never loaded by this command."""
from __future__ import annotations
import argparse
import hashlib
import json
import random
from pathlib import Path
import numpy as np
from manifest import load_manifest


def load_split(manifest: dict, base: Path, split: str, frames: int = 64):
    x, y = [], []
    for row in manifest['samples']:
        if row['split'] != split:
            continue
        sequence = np.load(base / row['features'], allow_pickle=False)
        if sequence.ndim != 3 or sequence.shape[1:] != (33, 4) or len(sequence) < 2 or not np.isfinite(sequence).all():
            raise ValueError('Features must be finite T×33×4 pose arrays with at least two frames')
        if manifest.get('coordinate_space') != 'world':
            raise ValueError('Expected world-coordinate training features')
        if np.any((sequence[:,:,3] < 0) | (sequence[:,:,3] > 1)):
            raise ValueError('Landmark visibility must be bounded between zero and one')
        if np.any(sequence[:,[11,12,23,24],3] < manifest['min_anchor_visibility']):
            raise ValueError('Unreliable normalization anchors require dataset review')
        # Translate by hip center and scale by shoulder span per frame. Visibility
        # remains unchanged; no imputed labels or invented coordinate channels.
        sequence = sequence.astype(np.float32, copy=True)
        center = (sequence[:, 23, :3] + sequence[:, 24, :3]) / 2
        scale = np.linalg.norm(sequence[:, 11, :3] - sequence[:, 12, :3], axis=-1)
        if np.any(scale < 1e-5):
            raise ValueError('Degenerate pose scale must be reviewed before training')
        sequence[:, :, :3] = (sequence[:, :, :3] - center[:, None, :]) / scale[:, None, None]
        indices = np.linspace(0, len(sequence)-1, frames).round().astype(int)
        x.append(sequence[indices].reshape(frames, 132))
        y.append(manifest['labels'].index(row['label']))
    return np.stack(x), np.asarray(y)


def build_tcn(class_count):
    import torch.nn as nn
    return nn.Sequential(nn.Conv1d(132, 64, 5, padding=2), nn.ReLU(),
        nn.Conv1d(64, 64, 5, padding=4, dilation=2), nn.ReLU(),
        nn.Conv1d(64, 64, 5, padding=8, dilation=4), nn.ReLU(),
        nn.AdaptiveAvgPool1d(1), nn.Flatten(), nn.Linear(64, class_count))


def train(path: Path, output: Path, epochs: int = 20):
    import torch
    from sklearn.metrics import f1_score
    from xgboost import XGBClassifier
    manifest = load_manifest(path)
    if epochs < 1 or epochs > 100:
        raise ValueError('Epochs must be between 1 and 100')
    random.seed(42); np.random.seed(42); torch.manual_seed(42)
    torch.set_num_threads(2)
    x, y = load_split(manifest, path.parent, 'train')
    vx, vy = load_split(manifest, path.parent, 'validation')
    def statistics(a):
        return np.concatenate([a.mean(1), a.std(1), a.min(1), a.max(1)], axis=1)
    tree = XGBClassifier(n_estimators=100, max_depth=4, n_jobs=2, random_state=42)
    tree.fit(statistics(x), y)
    model = build_tcn(len(manifest['labels']))
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = torch.nn.CrossEntropyLoss()
    tensor = torch.from_numpy(x).transpose(1, 2)
    target = torch.from_numpy(y).long()
    model.train()
    for _ in range(epochs):
        for indices in torch.randperm(len(x)).split(16):
            optimizer.zero_grad()
            loss_fn(model(tensor[indices]), target[indices]).backward()
            optimizer.step()
    model.eval()
    with torch.no_grad():
        predictions = model(torch.from_numpy(vx).transpose(1, 2)).argmax(1).numpy()
    metrics = {'boosted_tree': float(f1_score(vy, tree.predict(statistics(vx)), average='macro')),
               'temporal_convolution': float(f1_score(vy, predictions, average='macro'))}
    output.mkdir(parents=True, exist_ok=False)
    tree.save_model(output / 'boosted-tree.json')
    torch.save(model.state_dict(), output / 'temporal-convolution.pt')
    report = {'task': manifest['task'], 'seed': 42, 'labels': manifest['labels'],
              'manifest_digest': hashlib.sha256(path.read_bytes()).hexdigest(),
              'validation_macro_f1': metrics, 'holdout_evaluated': False, 'promotable': False,
              'selected_candidate': max(metrics, key=metrics.get)}
    (output / 'candidate.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('manifest', type=Path); parser.add_argument('output', type=Path)
    parser.add_argument('--epochs', type=int, default=20)
    args = parser.parse_args()
    print(json.dumps(train(args.manifest, args.output, args.epochs), indent=2))
