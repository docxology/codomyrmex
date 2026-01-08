from typing import Any, Optional

from abc import ABC, abstractmethod

from codomyrmex.cerebrum.cases import Case
from codomyrmex.cerebrum.exceptions import TransformationError
from codomyrmex.cerebrum.models import Model, ModelBase
from codomyrmex.logging_monitoring import get_logger






"""Model transformation and adaptation algorithms."""



logger = get_logger(__name__)


class ModelTransformer(ABC):
    """Base class for model transformations."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize transformer.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.logger = get_logger(__name__)

    @abstractmethod
    def transform(self, model: Model, transformation_type: str, **kwargs) -> Model:
        """Transform a model.

        Args:
            model: Model to transform
            transformation_type: Type of transformation
            **kwargs: Additional transformation parameters

        Returns:
            Transformed model
        """
        pass


class AdaptationTransformer(ModelTransformer):
    """Adapts models based on new cases."""

    def __init__(self, adaptation_rate: float = 0.1, config: Optional[dict[str, Any]] = None):
        """Initialize adaptation transformer.

        Args:
            adaptation_rate: Rate of adaptation (0-1)
            config: Additional configuration
        """
        super().__init__(config)
        self.adaptation_rate = adaptation_rate

    def transform(self, model: Model, transformation_type: str, **kwargs) -> Model:
        """Transform model through adaptation.

        Args:
            model: Model to adapt
            transformation_type: Type of adaptation
            **kwargs: Additional parameters (e.g., 'case' for case-based adaptation)

        Returns:
            Adapted model
        """
        if transformation_type == "adapt_to_case":
            case = kwargs.get("case")
            if not case:
                raise TransformationError("Case required for case-based adaptation")
            return self.adapt_to_case(model, case)
        elif transformation_type == "update_parameters":
            return self.update_parameters(model, kwargs.get("updates", {}))
        else:
            raise TransformationError(f"Unknown transformation type: {transformation_type}")

    def adapt_to_case(self, model: Model, case: Case) -> Model:
        """Adapt model to a new case.

        Args:
            model: Model to adapt
            case: Case to adapt to

        Returns:
            Adapted model
        """
        # Create adapted model
        adapted = Model(
            name=f"{model.name}_adapted",
            model_type=model.model_type,
            parameters=model.parameters.copy(),
            metadata=model.metadata.copy(),
        )

        # Adapt parameters based on case features
        # Simple adaptation: adjust parameters based on case features
        for feature, value in case.features.items():
            if isinstance(value, (int, float)):
                # Adjust parameter if it exists
                param_key = f"feature_{feature}"
                if param_key in adapted.parameters:
                    current = adapted.parameters[param_key]
                    adapted.parameters[param_key] = (
                        current * (1 - self.adaptation_rate) + value * self.adaptation_rate
                    )

        adapted.metadata["adaptation_history"] = adapted.metadata.get("adaptation_history", [])
        adapted.metadata["adaptation_history"].append(
            {"case_id": case.case_id, "adaptation_rate": self.adaptation_rate}
        )

        self.logger.debug(f"Adapted model {model.name} to case {case.case_id}")
        return adapted

    def update_parameters(self, model: Model, updates: dict[str, Any]) -> Model:
        """Update model parameters.

        Args:
            model: Model to update
            updates: Parameter updates

        Returns:
            Updated model
        """
        updated = Model(
            name=model.name,
            model_type=model.model_type,
            parameters={**model.parameters, **updates},
            metadata=model.metadata.copy(),
        )

        self.logger.debug(f"Updated parameters for model {model.name}")
        return updated


class LearningTransformer(ModelTransformer):
    """Updates models through learning from feedback."""

    def __init__(self, learning_rate: float = 0.01, config: Optional[dict[str, Any]] = None):
        """Initialize learning transformer.

        Args:
            learning_rate: Learning rate for parameter updates
            config: Additional configuration
        """
        super().__init__(config)
        self.learning_rate = learning_rate

    def transform(self, model: Model, transformation_type: str, **kwargs) -> Model:
        """Transform model through learning.

        Args:
            model: Model to learn
            transformation_type: Type of learning
            **kwargs: Additional parameters (e.g., 'feedback' for feedback-based learning)

        Returns:
            Learned model
        """
        if transformation_type == "learn_from_feedback":
            feedback = kwargs.get("feedback")
            if not feedback:
                raise TransformationError("Feedback required for learning")
            return self.learn_from_feedback(model, feedback)
        elif transformation_type == "gradient_update":
            gradient = kwargs.get("gradient", {})
            return self.gradient_update(model, gradient)
        else:
            raise TransformationError(f"Unknown transformation type: {transformation_type}")

    def learn_from_feedback(self, model: Model, feedback: dict[str, Any]) -> Model:
        """Learn from feedback.

        Args:
            model: Model to update
            feedback: Feedback dictionary with 'outcome', 'expected', 'error', etc.

        Returns:
            Updated model
        """
        # Create learned model
        learned = Model(
            name=f"{model.name}_learned",
            model_type=model.model_type,
            parameters=model.parameters.copy(),
            metadata=model.metadata.copy(),
        )

        # Simple learning: adjust parameters based on error
        error = feedback.get("error", 0.0)
        if isinstance(error, (int, float)):
            # Update parameters proportionally to error
            for param_key in learned.parameters:
                if isinstance(learned.parameters[param_key], (int, float)):
                    learned.parameters[param_key] += self.learning_rate * error

        learned.metadata["learning_history"] = learned.metadata.get("learning_history", [])
        learned.metadata["learning_history"].append(
            {"feedback": feedback, "learning_rate": self.learning_rate}
        )

        self.logger.debug(f"Learned from feedback for model {model.name}")
        return learned

    def gradient_update(self, model: Model, gradient: dict[str, Any]) -> Model:
        """Update model using gradient information.

        Args:
            model: Model to update
            gradient: Gradient dictionary

        Returns:
            Updated model
        """
        updated = Model(
            name=model.name,
            model_type=model.model_type,
            parameters=model.parameters.copy(),
            metadata=model.metadata.copy(),
        )

        # Apply gradient updates
        for param_key, grad_value in gradient.items():
            if param_key in updated.parameters:
                if isinstance(updated.parameters[param_key], (int, float)) and isinstance(
                    grad_value, (int, float)
                ):
                    updated.parameters[param_key] -= self.learning_rate * grad_value

        self.logger.debug(f"Applied gradient update to model {model.name}")
        return updated


class TransformationManager:
    """Manages model transformations."""

    def __init__(self):
        """Initialize transformation manager."""
        self.transformers: dict[str, ModelTransformer] = {}
        self.logger = get_logger(__name__)

    def register_transformer(self, name: str, transformer: ModelTransformer) -> None:
        """Register a transformer.

        Args:
            name: Transformer name
            transformer: Transformer instance
        """
        self.transformers[name] = transformer
        self.logger.debug(f"Registered transformer: {name}")

    def transform(
        self, model: Model, transformation_type: str, transformer_name: Optional[str] = None, **kwargs
    ) -> Model:
        """Transform a model.

        Args:
            model: Model to transform
            transformation_type: Type of transformation
            transformer_name: Specific transformer to use (optional)
            **kwargs: Transformation parameters

        Returns:
            Transformed model
        """
        if transformer_name:
            if transformer_name not in self.transformers:
                raise TransformationError(f"Transformer {transformer_name} not found")
            transformer = self.transformers[transformer_name]
        else:
            # Select appropriate transformer based on transformation type
            if transformation_type.startswith("adapt"):
                transformer = self.transformers.get("adaptation", AdaptationTransformer())
            elif transformation_type.startswith("learn"):
                transformer = self.transformers.get("learning", LearningTransformer())
            else:
                raise TransformationError(f"No transformer found for type: {transformation_type}")

        return transformer.transform(model, transformation_type, **kwargs)



