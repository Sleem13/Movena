from pydantic import BaseModel, Field
from app.schemas.error_schema import ErrorResponse


class GaitMetrics(BaseModel):
    step_count: int = 0
    gait_cycles: int = 0
    cadence_steps_per_min: float | None = None
    average_cycle_duration_sec: float | None = None
    average_stance_percent: float | None = None
    average_swing_percent: float | None = None
    temporal_symmetry_index: float | None = Field(default=None, description="Percent left-right cycle-duration difference.")
    stride_time_variability: float | None = Field(default=None, description="Coefficient of variation for stride/cycle duration.")
    relative_stride_excursion: float | None = Field(default=None, description="Normalized side-view foot excursion proxy, not meter-calibrated stride length.")
    average_knee_range_deg: float | None = None
    reference_dataset_notes: list[str] = Field(default_factory=list)


class BalanceMetrics(BaseModel):
    hold_duration_sec: float | None = None
    balance_mode: str = "unknown"
    sway_rms: float | None = Field(default=None, description="2D pose-derived body-sway proxy normalized by body height.")
    sway_max: float | None = None
    sway_path: float | None = None
    sway_velocity: float | None = None
    average_trunk_lean_deg: float | None = None
    max_trunk_lean_deg: float | None = None
    pelvis_tilt_mean: float | None = None
    knee_angle_variability_deg: float | None = None
    support_base_width: float | None = None
    foot_adjustment_index: float | None = None
    reference_dataset_notes: list[str] = Field(default_factory=list)


class FrameAnalysis(BaseModel):
    frame_index: int
    timestamp_sec: float
    knee_angle: float
    hip_angle: float
    trunk_angle: float
    phase: str
    detected_issue: str | None = None
    shoulder_angle: float | None = None
    elbow_angle: float | None = None
    hip_abduction_angle: float | None = None


class MLPrediction(BaseModel):
    enabled: bool = False
    predicted_label: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    model_name: str | None = None
    model_version: str = "sprint_5_baseline"
    model_mode: str | None = None
    provider_status: str | None = None
    feature_source: str | None = None
    supported_model_modes: list[str] = Field(default_factory=list)
    supported_exercises: list[str] = Field(default_factory=list)
    exercise_id: str | None = None
    warning: str
    ml_confidence_level: str | None = None
    agrees_with_rule_based: bool | None = None
    disagreement_note: str | None = None


class RepEvent(BaseModel):
    start_frame: int
    bottom_frame: int | None = None
    standing_frame: int | None = None
    end_frame: int
    duration_sec: float | None = None
    minimum_knee_angle: float | None = None
    maximum_knee_angle: float | None = None


class PartialRepEvent(BaseModel):
    start_frame: int
    end_frame: int
    reason: str


class PoseQuality(BaseModel):
    score: float = Field(ge=0, le=1)
    level: str
    total_frames: int
    pose_detected_frames: int
    pose_detection_rate: float = Field(ge=0, le=1)
    average_visibility: float = Field(ge=0, le=1)
    critical_landmark_visibility: float = Field(ge=0, le=1)
    missing_critical_landmark_rate: float = Field(ge=0, le=1)
    low_confidence_frames: int
    camera_view: str = "unknown"
    camera_view_warning: str | None = None
    warnings: list[str] = Field(default_factory=list)


class ScoreBreakdown(BaseModel):
    depth_score: int = Field(default=0, ge=0, le=100)
    knee_alignment_score: int = Field(default=0, ge=0, le=100)
    trunk_control_score: int = Field(default=0, ge=0, le=100)
    consistency_score: int = Field(default=0, ge=0, le=100)
    pose_confidence_score: int = Field(default=0, ge=0, le=100)
    completion_score: int | None = Field(default=None, ge=0, le=100)
    control_score: int | None = Field(default=None, ge=0, le=100)
    symmetry_placeholder_score: int | None = Field(default=None, ge=0, le=100)
    extension_range_score: int | None = Field(default=None, ge=0, le=100)
    posture_visibility_score: int | None = Field(default=None, ge=0, le=100)
    rep_completion_score: int | None = Field(default=None, ge=0, le=100)
    abduction_range_score: int | None = Field(default=None, ge=0, le=100)
    pelvis_trunk_stability_score: int | None = Field(default=None, ge=0, le=100)
    gait_phase_score: int | None = Field(default=None, ge=0, le=100)
    cadence_score: int | None = Field(default=None, ge=0, le=100)
    symmetry_score: int | None = Field(default=None, ge=0, le=100)
    stride_consistency_score: int | None = Field(default=None, ge=0, le=100)
    kinematic_range_score: int | None = Field(default=None, ge=0, le=100)
    hold_duration_score: int | None = Field(default=None, ge=0, le=100)
    sway_control_score: int | None = Field(default=None, ge=0, le=100)
    pelvis_control_score: int | None = Field(default=None, ge=0, le=100)
    knee_stability_score: int | None = Field(default=None, ge=0, le=100)


class AnalysisConfidence(BaseModel):
    score: float = Field(ge=0, le=1)
    level: str
    reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class InputValidity(BaseModel):
    is_valid: bool
    reason: str | None = None
    pose_detected_frames: int
    pose_detection_rate: float = Field(ge=0, le=1)
    overall_pose_detection_rate: float = Field(ge=0, le=1)
    critical_landmark_visibility: float = Field(ge=0, le=1)
    knee_angle_range: float
    hip_angle_range: float
    motion_variation: float
    valid_reps: int
    warnings: list[str] = Field(default_factory=list)
    shoulder_angle_range: float | None = None
    hip_abduction_angle_range: float | None = None


class AnalysisResponse(BaseModel):
    session_id: str | None = None
    exercise: str = "bodyweight_squat"
    exercise_id: str | None = None
    exercise_name: str | None = None
    status: str = "success"
    error_code: str | None = None
    message: str | None = None
    selected_exercise_id: str | None = None
    recognized_exercise_id: str | None = None
    recognition_confidence: float | None = Field(default=None, ge=0, le=1)
    recognition_status: str | None = None
    recognition_message: str | None = None
    auto_routed: bool = False
    total_reps: int = 0
    valid_reps: int | None = None
    average_knee_angle: float = 0
    average_hip_angle: float = 0
    average_trunk_angle: float = 0
    average_shoulder_angle: float | None = None
    average_elbow_angle: float | None = None
    average_hip_abduction_angle: float | None = None
    movement_score: int | None = Field(default=0, ge=0, le=100)
    rep_events: list[RepEvent] = Field(default_factory=list)
    partial_rep_events: list[PartialRepEvent] = Field(default_factory=list)
    rep_durations: list[float] = Field(default_factory=list)
    ignored_partial_reps: int = 0
    rep_count_confidence: float = Field(default=0, ge=0, le=1)
    phase_transitions: list[str] = Field(default_factory=list)
    pose_quality: PoseQuality | None = None
    score_breakdown: ScoreBreakdown | None = None
    analysis_confidence: AnalysisConfidence | None = None
    input_validity: InputValidity | None = None
    validation_warnings: list[str] = Field(default_factory=list)
    detected_issues: list[str] = Field(default_factory=list)
    feedback: list[str] = Field(default_factory=list)
    summary: str = ""
    limitations: list[str] = Field(default_factory=list)
    frame_analysis: list[FrameAnalysis] | None = None
    report_id: str | None = None
    report_download_url: str | None = None
    overlay_id: str | None = None
    overlay_preview_url: str | None = None
    overlay_download_url: str | None = None
    ml_prediction: MLPrediction | None = None
    gait_metrics: GaitMetrics | None = None
    balance_metrics: BalanceMetrics | None = None


SquatAnalysisResponse = AnalysisResponse
AnalysisErrorResponse = ErrorResponse
