"""Protected RehabRL decision-support endpoints.

The reinforcement-learning engine is embedded as a library. PhysioVision owns
authentication, authorization, CORS, error formatting, and application startup.
"""

from pathlib import Path
from typing import Any, Callable

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.dependencies.auth import require_super_admin, require_therapist
from app.api.error_responses import api_error_response
from rehabrl.api.errors import (
    CheckpointLoadError,
    CheckpointNotFoundError,
    InvalidInjuryError,
    RehabRLServiceError,
    TrainingInProgressError,
)
from rehabrl.api.schemas import AssessmentRequest, SimulationRequest, TrainingRequest
from rehabrl.api.service import RehabRLService

BACKEND_ROOT = Path(__file__).resolve().parents[3]
service = RehabRLService(BACKEND_ROOT)

router = APIRouter(
    prefix="/api/v1/rehab-rl",
    tags=["rehab-rl"],
    dependencies=[Depends(require_therapist)],
)

ERROR_STATUS = {
    InvalidInjuryError: 400,
    CheckpointNotFoundError: 404,
    CheckpointLoadError: 422,
    TrainingInProgressError: 409,
}


def _run(operation: Callable[[], Any]) -> Any | JSONResponse:
    try:
        return operation()
    except RehabRLServiceError as error:
        return api_error_response(
            type(error).__name__.upper(),
            str(error),
            ERROR_STATUS.get(type(error), 400),
        )


@router.get("/overview")
def overview() -> Any:
    return _run(service.overview)


@router.post("/assessment")
def assessment(request: AssessmentRequest) -> Any:
    return _run(lambda: service.assessment(request))


@router.post("/simulate")
def simulate(request: SimulationRequest) -> Any:
    return _run(lambda: service.simulate(request))


@router.get("/exercises")
def exercises() -> Any:
    return _run(service.exercises)


@router.get("/inspector", dependencies=[Depends(require_super_admin)])
def inspector() -> Any:
    return _run(service.inspector)


@router.post("/checkpoints/restore", dependencies=[Depends(require_super_admin)])
def restore_checkpoint() -> Any:
    return _run(service.restore_checkpoint)


@router.post("/training", dependencies=[Depends(require_super_admin)])
def start_training(request: TrainingRequest) -> Any:
    return _run(lambda: service.start_training(request))


@router.get("/training", dependencies=[Depends(require_super_admin)])
def training_status() -> Any:
    return _run(service.training_status)
