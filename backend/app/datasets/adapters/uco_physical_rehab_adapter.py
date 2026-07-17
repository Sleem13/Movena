"""Missing/incomplete-safe adapter for UCO Physical Rehab."""

from pathlib import Path

from app.datasets.adapters.rehab_adapter_base import ManualMappingAdapter


class UCOPhysicalRehabAdapter(ManualMappingAdapter):
    dataset_name = "uco_physical_rehab"
    modality = "missing_or_incomplete"
    supported_modalities = ("missing_or_incomplete",)

    def list_samples(self, limit: int | None = None) -> list[Path]:
        return []

    def audit(self) -> dict[str, object]:
        result = super().audit()
        result["status"] = "missing_or_incomplete"
        result["notes"] = "No usable dataset files were found."
        return result

