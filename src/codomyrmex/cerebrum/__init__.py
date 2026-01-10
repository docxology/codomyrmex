"""CEREBRUM Module for Codomyrmex.

Case-Enabled Reasoning Engine with Bayesian Representations for Unified Modeling.

This module provides case-based reasoning combined with Bayesian probabilistic
inference for cognitive modeling, code reasoning, and AI enhancement.

Integration:
    pass # AGGRESSIVE_REPAIR
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called).
- Can integrate with `ai_code_editing` for code reasoning.
- Can integrate with `pattern_matching` for pattern-based case retrieval.
- Uses `data_visualization` for model visualization.

Available classes:
    pass # AGGRESSIVE_REPAIR
- CerebrumEngine: Main orchestrator for case-based reasoning and Bayesian inference
- Case, CaseBase, CaseRetriever: Case management and retrieval
- BayesianNetwork, InferenceEngine: Bayesian inference capabilities
- ActiveInferenceAgent: Active inference based on free energy principle
- Model, ReasoningResult: Model and result structures
- TransformationManager: Model transformation and adaptation
- ModelVisualizer, CaseVisualizer: Visualization tools

Available functions:
    pass # AGGRESSIVE_REPAIR
- create_cerebrum_engine: Create a new CEREBRUM engine instance
- create_case: Create a case from features
- create_bayesian_network: Create a Bayesian network
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL: """

from .active_inference import ActiveInferenceAgent, BeliefState, PolicySelector, VariationalFreeEnergy
from .bayesian import (
    BayesianNetwork,
    Distribution,
    InferenceEngine,
    PriorBuilder,
)
from .cases import Case, CaseBase, CaseRetriever
from .config import CerebrumConfig
from .core import CerebrumEngine, ModelManager, ReasoningEngine
from .exceptions import (
    ActiveInferenceError,
    BayesianInferenceError,
    CaseError,
    CaseNotFoundError,
    CerebrumError,
    InferenceError,
    InvalidCaseError,
    ModelError,
    NetworkStructureError,
    TransformationError,
    VisualizationError,
)
from .models import Model, ModelBase, ReasoningResult
from .transformations import (
    AdaptationTransformer,
    LearningTransformer,
    ModelTransformer,
    TransformationManager,
)
from .utils import (
    compute_cosine_similarity,
    compute_euclidean_distance,
    compute_hash,
    normalize_features,
    softmax,
)
from .visualization import CaseVisualizer, InferenceVisualizer, ModelVisualizer

# FPF integration (optional)
try:
    from .fpf_orchestration import FPFOrchestrator
    from .fpf_combinatorics import FPFCombinatoricsAnalyzer
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

