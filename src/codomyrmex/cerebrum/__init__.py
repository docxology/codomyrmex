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
    InferenceError,
    InvalidCaseError,
    LearningTransformer,
    Model,
    ModelBase,
    ModelError,
    ModelManager,
    ModelTransformer,
    NetworkStructureError,
    ReasoningEngine,
    ReasoningResult,
    TransformationError,
    TransformationManager,
    VisualizationError,
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
from .visualization import CaseVisualizer, InferenceVisualizer, ModelVisualizer

# FPF integration (optional)
try:
    from .fpf import FPFCombinatoricsAnalyzer, FPFOrchestrator
    _HAS_FPF = True
except ImportError:
    _HAS_FPF = False
    FPFOrchestrator = None
    FPFCombinatoricsAnalyzer = None

__all__ = [
    # Core engine
    "CerebrumEngine",
    "ModelManager",
    "ReasoningEngine",
    # Case management
    "Case",
    "CaseBase",
    "CaseRetriever",
    # Bayesian inference
    "BayesianNetwork",
    "InferenceEngine",
    "Distribution",
    "PriorBuilder",
    # Active inference
    "ActiveInferenceAgent",
    "BeliefState",
    "VariationalFreeEnergy",
    "PolicySelector",
    # Models
    "Model",
    "ModelBase",
    "ReasoningResult",
    # Transformations
    "ModelTransformer",
    "AdaptationTransformer",
    "LearningTransformer",
    "TransformationManager",
    # Visualization
    "ModelVisualizer",
    "CaseVisualizer",
    "InferenceVisualizer",
    # Configuration
    "CerebrumConfig",
    # Exceptions
    "CerebrumError",
    "CaseError",
    "CaseNotFoundError",
    "InvalidCaseError",
    "BayesianInferenceError",
    "InferenceError",
    "NetworkStructureError",
    "ActiveInferenceError",
    "ModelError",
    "TransformationError",
    "VisualizationError",
    # Utilities
    "compute_hash",
    "normalize_features",
    "compute_euclidean_distance",
    "compute_cosine_similarity",
    "softmax",
]

# Add FPF integration if available
if _HAS_FPF:
    __all__.extend(["FPFOrchestrator", "FPFCombinatoricsAnalyzer"])

__version__ = "0.1.0"
