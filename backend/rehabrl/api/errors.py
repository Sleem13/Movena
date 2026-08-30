"""Domain-level errors raised by the RehabRL service layer."""


class RehabRLServiceError(Exception):
    """Base class for service failures that can be returned to API clients."""


class InvalidInjuryError(RehabRLServiceError):
    """Raised when a request contains an unsupported injury type."""


class CheckpointNotFoundError(RehabRLServiceError):
    """Raised when no compatible model checkpoint exists."""


class CheckpointLoadError(RehabRLServiceError):
    """Raised when an existing checkpoint cannot be loaded."""


class TrainingInProgressError(RehabRLServiceError):
    """Raised when a new run is requested while training is active."""
