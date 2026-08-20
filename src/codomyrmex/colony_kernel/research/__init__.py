"""Offline-first Colony Kernel research harnesses.

Research adapters are deliberately separate from production actuation.  They
produce manifests and traces suitable for replay; they do not contact external
providers unless a caller explicitly supplies a live adapter.
"""

from .active_inference_adapter import (
    ActiveInferenceDecision,
    ColonyActiveInferenceAdapter,
    create_default_colony_generative_model,
)
from .actuation_adapter import (
    ActuationObservationResult,
    ActuationStatus,
    ExternalActuationAdapter,
    ExternalExecutionWitness,
)
from .adversarial_workload import (
    AdversarialBenchmarkReport,
    AdversarialWorkloadEvaluator,
    ThreatStratifiedResult,
    load_adversarial_cases_from_json,
)
from .benchmark import (
    AgentDojoAdapter,
    BenchmarkRun,
    ExternalBenchmarkAdapter,
    InjecAgentAdapter,
    ToolEmuAdapter,
    generate_synthetic_cases,
    run_paired_benchmark,
)
from .calibration_study import (
    CalibrationRecord,
    TrustCalibrationReport,
    TrustCalibrationStudy,
)
from .concurrency_study import (
    ConcurrencyAuditReport,
    CrashRecoveryReport,
    PersistenceConcurrencyStudy,
)
from .metrics import (
    brier_score,
    confidence_interval,
    expected_calibration_error,
    log_loss,
    paired_bootstrap_delta,
    reliability_bins,
    selective_risk,
)
from .persistent_store import PersistentPheromoneStore
from .probabilistic import (
    GenerativeModelSpec,
    KernelObservation,
    KernelProbabilisticAdapter,
)
from .schemas import (
    PolicyTrace,
    ResearchManifest,
    TaskCase,
    split_leakage_report,
)

__all__ = [
    "ActiveInferenceDecision",
    "ActuationObservationResult",
    "ActuationStatus",
    "AdversarialBenchmarkReport",
    "AdversarialWorkloadEvaluator",
    "AgentDojoAdapter",
    "BenchmarkRun",
    "CalibrationRecord",
    "ColonyActiveInferenceAdapter",
    "ConcurrencyAuditReport",
    "CrashRecoveryReport",
    "ExternalActuationAdapter",
    "ExternalBenchmarkAdapter",
    "ExternalExecutionWitness",
    "GenerativeModelSpec",
    "InjecAgentAdapter",
    "KernelObservation",
    "KernelProbabilisticAdapter",
    "PersistenceConcurrencyStudy",
    "PersistentPheromoneStore",
    "PolicyTrace",
    "ResearchManifest",
    "TaskCase",
    "ThreatStratifiedResult",
    "ToolEmuAdapter",
    "TrustCalibrationReport",
    "TrustCalibrationStudy",
    "brier_score",
    "confidence_interval",
    "create_default_colony_generative_model",
    "expected_calibration_error",
    "generate_synthetic_cases",
    "load_adversarial_cases_from_json",
    "log_loss",
    "paired_bootstrap_delta",
    "reliability_bins",
    "run_paired_benchmark",
    "selective_risk",
    "split_leakage_report",
]
