"""Core Cerebrum reasoning logic and engine."""

from .cases import Case, CaseBase, CaseRetriever
from .chain import ChainExecutionResult, ReasoningChain
from .config import CerebrumConfig
from .core import CerebrumEngine, ModelManager, ReasoningEngine
from .decision import Decision, DecisionModule
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
from .memory import WorkingMemory
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
