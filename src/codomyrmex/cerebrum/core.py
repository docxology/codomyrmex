"""Main CEREBRUM engine that orchestrates case-based reasoning and Bayesian inference."""

from typing import Any, Optional

from codomyrmex.cerebrum.active_inference import ActiveInferenceAgent
from codomyrmex.cerebrum.bayesian import BayesianNetwork, InferenceEngine, PriorBuilder
from codomyrmex.cerebrum.cases import Case, CaseBase, CaseRetriever
from codomyrmex.cerebrum.config import CerebrumConfig
from codomyrmex.cerebrum.exceptions import CerebrumError, ModelError
from codomyrmex.cerebrum.models import Model, ReasoningResult
from codomyrmex.cerebrum.transformations import (
    AdaptationTransformer,
    LearningTransformer,
    TransformationManager,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class ModelManager:
    """Manages multiple cognitive models."""

    def __init__(self):
        """Initialize model manager."""
        self.models: dict[str, Model] = {}
        self.logger = get_logger(__name__)

    def create_model(self, name: str, model_type: str, config: Optional[dict[str, Any]] = None) -> Model:
        """Create a new model.

        Args:
            name: Model name
            model_type: Type of model
            config: Model configuration

        Returns:
            Created model
        """
        if name in self.models:
            raise ModelError(f"Model {name} already exists")

        model = Model(name=name, model_type=model_type, parameters=config or {})
        self.models[name] = model
        self.logger.info(f"Created model: {name} ({model_type})")
        return model

    def get_model(self, name: str) -> Model:
        """Get a model by name.

        Args:
            name: Model name

        Returns:
            Model object

        Raises:
            ModelError: If model not found
        """
        if name not in self.models:
            raise ModelError(f"Model {name} not found")
        return self.models[name]

    def remove_model(self, name: str) -> None:
        """Remove a model.

        Args:
            name: Model name
        """
        if name in self.models:
            del self.models[name]
            self.logger.debug(f"Removed model: {name}")

    def list_models(self) -> list[str]:
        """List all model names."""
        return list(self.models.keys())


class ReasoningEngine:
    """Combines case retrieval with probabilistic inference."""

    def __init__(
        self,
        case_base: CaseBase,
        bayesian_network: Optional[BayesianNetwork] = None,
        config: Optional[CerebrumConfig] = None,
    ):
        """Initialize reasoning engine.

        Args:
            case_base: Case base for case-based reasoning
            bayesian_network: Optional Bayesian network for probabilistic inference
            config: Configuration
        """
        self.case_base = case_base
        self.bayesian_network = bayesian_network
        self.config = config or CerebrumConfig()

        self.case_retriever = CaseRetriever(
            case_base, weighting_strategy=self.config.case_weighting_strategy
        )

        self.inference_engine: Optional[InferenceEngine] = None
        if bayesian_network:
            self.inference_engine = InferenceEngine(
                bayesian_network, method=self.config.inference_method
            )

        self.logger = get_logger(__name__)

    def reason(self, query: Case, context: Optional[dict[str, Any]] = None) -> ReasoningResult:
        """Perform reasoning combining case-based and Bayesian inference.

        Args:
            query: Query case
            context: Additional context

        Returns:
            Reasoning result
        """
        context = context or {}

        # Case-based reasoning: retrieve similar cases
        similar_cases = self.case_retriever.retrieve(
            query, k=self.config.max_retrieved_cases, threshold=self.config.case_similarity_threshold
        )

        # Extract outcomes from similar cases
        outcomes = []
        for case, similarity in similar_cases:
            if case.outcome is not None:
                outcomes.append((case.outcome, similarity))

        # Compute prediction from case outcomes
        if outcomes:
            # Weight outcomes by similarity
            total_weight = sum(sim for _, sim in outcomes)
            if total_weight > 0:
                weighted_outcome = sum(outcome * sim for outcome, sim in outcomes) / total_weight
                confidence = min(1.0, total_weight / len(outcomes))
            else:
                weighted_outcome = outcomes[0][0] if outcomes else None
                confidence = 0.0
        else:
            weighted_outcome = None
            confidence = 0.0

        # Bayesian inference if network available
        inference_results = {}
        if self.inference_engine and self.bayesian_network:
            try:
                # Convert query features to evidence
                evidence = {k: v for k, v in query.features.items() if isinstance(v, (int, float, str))}

                # Perform inference
                query_vars = {var: None for var in self.bayesian_network.nodes if var not in evidence}
                if query_vars:
                    inference_results = self.inference_engine.infer(query_vars, evidence)

                    # Update prediction if inference provides better estimate
                    if inference_results:
                        # Use mode of most confident distribution
                        best_var = max(
                            inference_results.keys(),
                            key=lambda v: max(inference_results[v].probabilities),
                        )
                        best_dist = inference_results[best_var]
                        if weighted_outcome is None or best_dist.probabilities[0] > confidence:
                            weighted_outcome = best_dist.mode()
                            confidence = max(best_dist.probabilities)
            except Exception as e:
                self.logger.warning(f"Bayesian inference failed: {e}")

        return ReasoningResult(
            prediction=weighted_outcome,
            confidence=confidence,
            evidence=context,
            retrieved_cases=[case for case, _ in similar_cases],
            inference_results=inference_results,
            metadata={"num_retrieved": len(similar_cases)},
        )


class CerebrumEngine:
    """Main CEREBRUM engine orchestrating all components."""

    def __init__(self, config: Optional[CerebrumConfig] = None):
        """Initialize CEREBRUM engine.

        Args:
            config: Configuration
        """
        self.config = config or CerebrumConfig()
        self.logger = get_logger(__name__)

        # Core components
        self.case_base = CaseBase()
        self.model_manager = ModelManager()
        self.transformation_manager = TransformationManager()

        # Register default transformers
        self.transformation_manager.register_transformer(
            "adaptation", AdaptationTransformer(adaptation_rate=self.config.adaptation_rate)
        )
        self.transformation_manager.register_transformer(
            "learning", LearningTransformer(learning_rate=self.config.learning_rate)
        )

        # Optional components
        self.bayesian_network: Optional[BayesianNetwork] = None
        self.active_inference_agent: Optional[ActiveInferenceAgent] = None
        self.reasoning_engine: Optional[ReasoningEngine] = None

        self.logger.info("Initialized CEREBRUM engine")

    def create_model(self, name: str, model_type: str, config: Optional[dict[str, Any]] = None) -> Model:
        """Create a new cognitive model.

        Args:
            name: Model name
            model_type: Type of model
            config: Model configuration

        Returns:
            Created model
        """
        return self.model_manager.create_model(name, model_type, config)

    def add_case(self, case: Case) -> None:
        """Add a case to the case base.

        Args:
            case: Case to add
        """
        self.case_base.add_case(case)
        self.logger.debug(f"Added case: {case.case_id}")

    def reason(self, case: Case, context: Optional[dict[str, Any]] = None) -> ReasoningResult:
        """Perform reasoning on a case.

        Args:
            case: Query case
            context: Additional context

        Returns:
            Reasoning result
        """
        # Initialize reasoning engine if needed
        if self.reasoning_engine is None:
            self.reasoning_engine = ReasoningEngine(
                self.case_base, self.bayesian_network, self.config
            )

        return self.reasoning_engine.reason(case, context)

    def learn_from_case(self, case: Case, outcome: Any) -> None:
        """Learn from a case by updating the case base.

        Args:
            case: Case to learn from
            outcome: Observed outcome
        """
        case.outcome = outcome
        self.case_base.add_case(case)
        self.logger.debug(f"Learned from case: {case.case_id}")

    def transform_model(
        self, model: Model, transformation: str, **kwargs
    ) -> Model:
        """Transform a model.

        Args:
            model: Model to transform
            transformation: Transformation type
            **kwargs: Transformation parameters

        Returns:
            Transformed model
        """
        return self.transformation_manager.transform(model, transformation, **kwargs)

    def set_bayesian_network(self, network: BayesianNetwork) -> None:
        """Set Bayesian network for probabilistic inference.

        Args:
            network: Bayesian network
        """
        self.bayesian_network = network
        # Reinitialize reasoning engine with new network
        self.reasoning_engine = ReasoningEngine(
            self.case_base, self.bayesian_network, self.config
        )
        self.logger.info(f"Set Bayesian network: {network.name}")

    def set_active_inference_agent(self, agent: ActiveInferenceAgent) -> None:
        """Set active inference agent.

        Args:
            agent: Active inference agent
        """
        self.active_inference_agent = agent
        self.logger.info("Set active inference agent")

    def get_case_base(self) -> CaseBase:
        """Get the case base."""
        return self.case_base

    def get_model_manager(self) -> ModelManager:
        """Get the model manager."""
        return self.model_manager

    def to_dict(self) -> dict[str, Any]:
        """Convert engine state to dictionary."""
        return {
            "config": self.config.to_dict(),
            "case_base": self.case_base.to_dict(),
            "models": {name: model.to_dict() for name, model in self.model_manager.models.items()},
            "bayesian_network": self.bayesian_network.to_dict() if self.bayesian_network else None,
        }


