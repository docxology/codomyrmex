"""Offline-first Colony Kernel research harnesses.

Research adapters are deliberately separate from production actuation.  They
produce manifests and traces suitable for replay; they do not contact external
providers unless a caller explicitly supplies a live adapter.
"""

from .benchmark import (
    AgentDojoAdapter,
    BenchmarkRun,
    ExternalBenchmarkAdapter,
    InjecAgentAdapter,
    ToolEmuAdapter,
    generate_synthetic_cases,
    run_paired_benchmark,
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
    "AgentDojoAdapter",
    "BenchmarkRun",
    "ExternalBenchmarkAdapter",
    "GenerativeModelSpec",
    "InjecAgentAdapter",
    "KernelObservation",
    "KernelProbabilisticAdapter",
    "PersistentPheromoneStore",
    "PolicyTrace",
    "ResearchManifest",
    "TaskCase",
    "ToolEmuAdapter",
    "brier_score",
    "confidence_interval",
    "expected_calibration_error",
    "generate_synthetic_cases",
    "log_loss",
    "paired_bootstrap_delta",
    "reliability_bins",
    "run_paired_benchmark",
    "selective_risk",
    "split_leakage_report",
]
