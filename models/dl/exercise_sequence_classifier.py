"""Temporal pose classifier used by the PhysioVision sequence-training pipeline."""

from __future__ import annotations

try:
    import torch
    from torch import nn
except ImportError:  # pragma: no cover - exercised only without the optional ML environment
    torch = None
    nn = None


if nn is not None:
    class ExerciseSequenceClassifier(nn.Module):
        """Bidirectional GRU with learned temporal attention."""

        def __init__(
            self,
            input_size: int,
            hidden_size: int,
            num_classes: int,
            *,
            num_layers: int = 2,
            dropout: float = 0.25,
        ) -> None:
            super().__init__()
            self.encoder = nn.GRU(
                input_size,
                hidden_size,
                num_layers=num_layers,
                batch_first=True,
                bidirectional=True,
                dropout=dropout if num_layers > 1 else 0.0,
            )
            encoded_size = hidden_size * 2
            self.attention = nn.Linear(encoded_size, 1)
            self.head = nn.Sequential(
                nn.LayerNorm(encoded_size),
                nn.Linear(encoded_size, hidden_size),
                nn.GELU(),
                nn.Dropout(dropout),
                nn.Linear(hidden_size, num_classes),
            )

        def forward(self, inputs: torch.Tensor) -> torch.Tensor:
            encoded, _ = self.encoder(inputs)
            weights = torch.softmax(self.attention(encoded), dim=1)
            pooled = torch.sum(encoded * weights, dim=1)
            return self.head(pooled)
else:
    class ExerciseSequenceClassifier:  # pragma: no cover
        def __init__(self, *_args, **_kwargs) -> None:
            raise RuntimeError("PyTorch is optional. Install requirements-ml.txt to enable DL training.")
