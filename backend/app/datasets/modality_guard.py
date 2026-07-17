"""Fail-closed modality routing for all dataset training tracks."""
from dataclasses import dataclass
from pathlib import Path

VIDEO_EXTENSIONS={".mp4",".avi",".mov",".mkv",".webm"};IMAGE_EXTENSIONS={".jpg",".jpeg",".png",".bmp"}
PIPELINES={
 "video_pose_pipeline":{"video","image"}, "skeleton_sequence_pipeline":{"skeleton_2d","skeleton_3d"},
 "sensor_timeseries_pipeline":{"sensor_timeseries"}, "image_pose_pipeline":{"image"},
 "tabular_feature_pipeline":{"tabular_features"},
}
ALLOWED_MODALITIES={"video":PIPELINES["video_pose_pipeline"],"mediapipe_pose":PIPELINES["video_pose_pipeline"],"sensor_timeseries":{"sensor_timeseries"},"skeleton":{"skeleton_2d","skeleton_3d"}}
class IncompatibleModalityError(ValueError):pass
@dataclass(frozen=True)
class ModalityGuardResult:
    allowed:bool;reason:str
    def to_dict(self):return {"allowed":self.allowed,"reason":self.reason}
def infer_file_modality(path):
    suffix=Path(path).suffix.lower()
    if suffix in VIDEO_EXTENSIONS:return "video"
    if suffix in IMAGE_EXTENSIONS:return "image"
    if suffix in {".mat",".txt",".tsv"}:return "sensor_timeseries"
    if suffix in {".npy",".npz",".pkl"}:return "skeleton_3d"
    if suffix==".csv":return "tabular_features"
    return "unknown"
def check_modality_compatibility(modality,pipeline_name,dataset_status="ready"):
    if pipeline_name not in PIPELINES:return ModalityGuardResult(False,f"unknown pipeline: {pipeline_name}")
    if dataset_status=="missing_or_incomplete":return ModalityGuardResult(False,"missing_or_incomplete datasets cannot enter training")
    if modality in {"mixed","unknown","missing_or_incomplete","missing"}:return ModalityGuardResult(False,f"{modality} requires an adapter and manual review")
    allowed=modality in PIPELINES[pipeline_name]
    return ModalityGuardResult(allowed,"compatible" if allowed else f"{modality} cannot be used in {pipeline_name}")
def ensure_pipeline_compatible(path,pipeline,declared_modality=None):
    aliases={"video":"video_pose_pipeline","mediapipe_pose":"video_pose_pipeline","skeleton":"skeleton_sequence_pipeline"};target=aliases.get(pipeline,pipeline)
    result=check_modality_compatibility(declared_modality or infer_file_modality(path),target)
    if not result.allowed:raise IncompatibleModalityError(result.reason)
    return declared_modality or infer_file_modality(path)
