"""CEREBRUM Module for Codomyrmex.

Case-Enabled Reasoning Engine with Bayesian Representations for Unified Modeling.

This module provides case-based reasoning combined with Bayesian probabilistic
inference for cognitive modeling, code reasoning, and AI enhancement.

Integration:
    pass
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called).
- Can integrate with `ai_code_editing` for code reasoning.
- Can integrate with `pattern_matching` for pattern-based case retrieval.
- Uses `data_visualization` for model visualization.

Available classes:
    pass
- CerebrumEngine: Main orchestrator for case-based reasoning and Bayesian inference
- Case, CaseBase, CaseRetriever: Case management and retrieval
- BayesianNetwork, InferenceEngine: Bayesian inference capabilities
- ActiveInferenceAgent: Active inference based on free energy principle
- Model, ReasoningResult: Model and result structures
- TransformationManager: Model transformation and adaptation
- ModelVisualizer, CaseVisualizer: Visualization tools

Available functions:
    pass
- create_cerebrum_engine: Create a new CEREBRUM engine instance
- create_case: Create a case from features
- create_bayesian_network: Create a Bayesian network
"""

# Shared schemas for cross-module interop
import contextlib

with contextlib.suppress(ImportError):
    from codomyrmex.validation.schemas import Result, ResultStatus

from .core import (
    ActiveInferenceError,
    AdaptationTransformer,
    BayesianInferenceError,
    Case,
    CaseBase,
    CaseError,
    CaseNotFoundError,
    CaseRetriever,
    CerebrumConfig,
    CerebrumEngine,
    CerebrumError,
    ChainExecutionResult,
    Decision,
    DecisionModule,
    InferenceError,
    InvalidCaseError,
    LearningTransformer,
    Model,
    ModelBase,
    ModelError,
    ModelManager,
    ModelTransformer,
    NetworkStructureError,
    ReasoningChain,
    ReasoningEngine,
    ReasoningResult,
    TransformationError,
    TransformationManager,
    VisualizationError,
    WorkingMemory,
    compute_cosine_similarity,
    compute_euclidean_distance,
    compute_hash,
    normalize_features,
    softmax,
)
from .inference import (
    ActiveInferenceAgent,
    BayesianNetwork,
    BeliefState,
    Distribution,
    InferenceEngine,
    PolicySelector,
    PriorBuilder,
    VariationalFreeEnergy,
)
from .inference.free_energy_loop import FreeEnergyLoop, LoopResult, StepResult
from .inference.hierarchical_planner import (
    HierarchicalPlan,
    HierarchicalPlanner,
    LevelResult,
    PlanLevel,
)
from .visualization import CaseVisualizer, InferenceVisualizer, ModelVisualizer

# FPF integration (optional)
try:
    from .fpf import FPFCombinatoricsAnalyzer, FPFOrchestrator

    _HAS_FPF = True
except ImportError:
    _HAS_FPF = False


def cli_commands():
    """Return CLI commands for the cerebrum module."""
    return {
        "status": {
            "help": "Show cerebrum engine status",
            "handler": lambda **kwargs: print(
                f"CEREBRUM Engine v{__version__}\n"
                f"  FPF integration: {'available' if _HAS_FPF else 'not available'}\n"
                f"  Components: CerebrumEngine, BayesianNetwork, ActiveInferenceAgent\n"
                f"  Status: ready"
            ),
        },
        "infer": {
            "help": "Run inference using the CEREBRUM engine",
            "handler": lambda **kwargs: print(
                "CEREBRUM Inference\n"
                "  Available engines: BayesianNetwork, InferenceEngine, ActiveInferenceAgent\n"
                "  Use CerebrumEngine.create() to start a session"
            ),
        },
    }


__all__ = [
    # Active inference
    "ActiveInferenceAgent",
    "ActiveInferenceError",
    "AdaptationTransformer",
    "BayesianInferenceError",
    # Bayesian inference
    "BayesianNetwork",
    "BeliefState",
    # Case management
    "Case",
    "CaseBase",
    "CaseError",
    "CaseNotFoundError",
    "CaseRetriever",
    "CaseVisualizer",
    # Configuration
    "CerebrumConfig",
    # Core engine
    "CerebrumEngine",
    # Exceptions
    "CerebrumError",
    "ChainExecutionResult",
    "Decision",
    "DecisionModule",
    "Distribution",
    # Free-energy loop (v1.3.0)
    "FreeEnergyLoop",
    # Hierarchical planner (v1.3.1)
    "HierarchicalPlan",
    "HierarchicalPlanner",
    "InferenceEngine",
    "InferenceError",
    "InferenceVisualizer",
    "InvalidCaseError",
    "LearningTransformer",
    "LevelResult",
    "LoopResult",
    # Models
    "Model",
    "ModelBase",
    "ModelError",
    "ModelManager",
    # Transformations
    "ModelTransformer",
    # Visualization
    "ModelVisualizer",
    "NetworkStructureError",
    "PlanLevel",
    "PolicySelector",
    "PriorBuilder",
    "ReasoningChain",
    "ReasoningEngine",
    "ReasoningResult",
    "StepResult",
    "TransformationError",
    "TransformationManager",
    "VariationalFreeEnergy",
    "VisualizationError",
    "WorkingMemory",
    # CLI integration
    "cli_commands",
    "compute_cosine_similarity",
    "compute_euclidean_distance",
    # Utilities
    "compute_hash",
    "normalize_features",
    "softmax",
]

# Add FPF integration if available
if _HAS_FPF:
    __all__.extend(["FPFCombinatoricsAnalyzer", "FPFOrchestrator"])

__version__ = "0.3.0"
