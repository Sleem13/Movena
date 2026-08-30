"""HTTP routes for the RehabRL API."""

from typing import Any

from fastapi import APIRouter

from .schemas import AssessmentRequest, SimulationRequest, TrainingRequest
from .service import RehabRLService


def create_api_router(service: RehabRLService) -> APIRouter:
    """Create API routes bound to a service instance."""
    router = APIRouter(prefix="/api")

    @router.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @router.get("/overview")
    def overview() -> dict[str, Any]:
        return service.overview()

    @router.get("/checkpoints")
    def checkpoints() -> list[dict[str, Any]]:
        return service.checkpoints()

    @router.post("/checkpoints/restore")
    def restore_checkpoint() -> dict[str, Any]:
        return service.restore_checkpoint()

    @router.post("/assessment")
    def assessment(request: AssessmentRequest) -> dict[str, Any]:
        return service.assessment(request)

    @router.post("/simulate")
    def simulate(request: SimulationRequest) -> dict[str, Any]:
        return service.simulate(request)

    @router.get("/exercises")
    def exercises() -> dict[str, Any]:
        return service.exercises()

    @router.get("/inspector")
    def inspector() -> dict[str, Any]:
        return service.inspector()

    @router.post("/training")
    def start_training(request: TrainingRequest) -> dict[str, Any]:
        return service.start_training(request)

    @router.get("/training")
    def training_status() -> dict[str, Any]:
        return service.training_status()

    return router
