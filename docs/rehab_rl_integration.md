# RehabRL integration

## Status

RehabRL is embedded in PhysioVision AI as an experimental, protected clinical
decision-support module. The integration reuses PhysioVision authentication,
role authorization, CORS, error responses, navigation, deployment, and logging.
The standalone RehabRL FastAPI server and React shell are not mounted.

The workspace is available at `/rehab-policy`. It provides:

- Policy/runtime overview.
- Clinician-entered patient-state assessment.
- Stage-aware prescription candidates with confidence and risk indicators.
- Synthetic recovery-trajectory simulation.
- Prescription exercise exploration.
- Super-admin model inspection, checkpoint restore, and background training.

## Architecture

```text
PhysioVision React workspace
        |
        | Bearer token
        v
/api/v1/rehab-rl router
        |
        +--> PhysioVision role authorization
        |
        +--> RehabRL service facade
                  |
                  +--> trained NumPy policy on CPU-only deployments
                  +--> trained PyTorch policy when CUDA is available
                  +--> clinical heuristic if no compatible checkpoint exists
```

The reusable engine lives in `backend/rehabrl`. Checkpoints and training history
live in `backend/checkpoints`. The Dockerfile copies the whole `backend`
directory, so the package and both checkpoint formats are included in the API
image without additional copy rules.

## Access control

| Capability | Patient | Therapist | Admin | Super admin |
|---|---:|---:|---:|---:|
| Open RehabRL workspace | No | Yes | Yes | Yes |
| View policy overview and exercise library | No | Yes | Yes | Yes |
| Generate assessment and simulation output | No | Yes | Yes | Yes |
| Inspect model internals | No | No | No | Yes |
| Restore a checkpoint | No | No | No | Yes |
| Start or monitor training | No | No | No | Yes |

The API enforces these rules independently of frontend navigation. A patient or
anonymous caller receives the platform's standard authentication/authorization
error response.

## API contract

All endpoints use the `/api/v1/rehab-rl` prefix.

| Method | Path | Minimum role | Purpose |
|---|---|---|---|
| `GET` | `/overview` | Therapist/admin | Policy metrics, runtime, checkpoint, and reference trajectory |
| `POST` | `/assessment` | Therapist/admin | Generate a reviewable prescription candidate |
| `POST` | `/simulate` | Therapist/admin | Run a synthetic recovery trajectory |
| `GET` | `/exercises` | Therapist/admin | List policy exercise definitions and injury categories |
| `GET` | `/inspector` | Super admin | Inspect architecture, configuration, statistics, and sampled weights |
| `POST` | `/checkpoints/restore` | Super admin | Restore the compatible best-model checkpoint |
| `POST` | `/training` | Super admin | Start a background training run |
| `GET` | `/training` | Super admin | Read current training progress |

Assessment inputs are normalized to `0..1` where applicable and validated by
Pydantic. Recovery stage is an integer from `0` (Acute) through `4` (Return).

## Runtime and checkpoint selection

Two compatible policy artifacts are packaged:

- `backend/checkpoints/best_model.pt` for PyTorch/CUDA.
- `backend/checkpoints/best_model.pt.npy` for NumPy/CPU.

The runtime selects PyTorch only when PyTorch is installed and CUDA is
available. CPU-only production images therefore use the NumPy implementation
without adding the large PyTorch runtime. The overview response reports the
actual backend, device, and whether the recommendation source is a trained
policy or the clinical heuristic fallback.

## Local development

Start the normal PhysioVision backend and frontend; no second RehabRL server is
needed.

```powershell
.\scripts\start_backend.ps1 -Reload

Set-Location frontend
npm run dev
```

Sign in as a therapist, admin, or super administrator and open
`http://127.0.0.1:5173/rehab-policy`.

## Verification baseline

The integration was verified on 2026-08-30 with:

- Original RehabRL focused suite: 17 passed.
- Complete PhysioVision backend suite: 305 passed.
- PhysioVision frontend suite: 134 passed.
- Vite production build: passed; RehabRL is emitted as a lazy-loaded chunk.
- Repository-root and staging startup without optional ML runtimes: passed.
- CPU/container-layout check: NumPy trained policy loaded successfully.
- Rendered desktop and 390×844 mobile assessment workflow: passed with no
  relevant console warnings or errors.

Reproduce the core checks:

```powershell
.\.venv\Scripts\python.exe -m pytest -q

Set-Location frontend
npm test -- --run
npm run build
```

## Operational considerations

- Training runs execute in a background thread inside the API process. Do not
  rely on this mechanism for durable production training jobs; process restart
  terminates the worker.
- A running training job is local to one API instance. Multiple replicas do not
  share status or locks.
- Checkpoints are local filesystem artifacts. Ephemeral hosts require external
  artifact storage or an immutable image release.
- Recommendations are not yet persisted as versioned clinical records and are
  not automatically linked to a patient's care plan.
- The packaged model is an experimental research artifact. Simulation reward is
  not evidence of clinical effectiveness.

## Safety and clinical limitations

RehabRL output must be reviewed by a qualified clinician. It must not be used
as an autonomous prescription, diagnosis, emergency recommendation, or promise
of patient outcome. Before real-patient use, complete the clinical, security,
privacy, bias, and model-governance gates in the
[RehabRL improvement roadmap](rehab_rl_improvement_roadmap.md) and the existing
[care-platform launch gate](care_platform_launch_gate.md).

## License

The embedded RehabRL source retains its upstream Apache License 2.0 at
`backend/rehabrl/LICENSE`. PhysioVision AI retains its repository-level license.
