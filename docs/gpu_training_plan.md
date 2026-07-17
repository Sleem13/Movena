# GPU Training Plan

The available NVIDIA RTX 2000 Ada Generation GPU with approximately 16 GB of memory is suitable for controlled PyTorch feature, sequence, and architecture experiments. GPU availability accelerates computation; it does not make a dataset complete, labels reliable, evaluation leakage-safe, or a model clinically valid.

The current recognition feature set has only one training-ready exercise class (`bodyweight_squat`). Exercise-recognition training must therefore remain refused even when CUDA is available. GPU code must not bypass class-count, manual-review, participant-grouping, model-card, or promotion gates.

## Recommended order

1. Run `python scripts/check_gpu_environment.py`.
2. Run the short synthetic CPU/CUDA benchmark.
3. Run synthetic sequence training as a software and device smoke test.
4. Consider real training only after at least two clean, sufficiently represented classes exist.
5. Use participant-grouped train/validation/holdout evaluation.
6. Complete error analysis and a model card before any app integration decision.

```powershell
python scripts/benchmark_gpu_training.py --dry-run
python scripts/benchmark_gpu_training.py --steps 20
python models/dl/train_sequence_model.py --synthetic --device auto --epochs 2 --batch-size 16
```

Synthetic loss, accuracy, throughput, and GPU speedup are infrastructure results only. They do not measure real exercise recognition or movement quality.

