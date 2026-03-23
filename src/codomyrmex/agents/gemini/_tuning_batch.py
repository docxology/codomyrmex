"""Mixin for Gemini model tuning and batch operations."""

from typing import Any

from google.genai import types

from codomyrmex.agents.core.exceptions import GeminiError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class GeminiTuningBatchMixin:
    """Model tuning (fine-tuning) and batch inference operations.

    Requires ``client`` and ``default_model`` from the host class.
    """

    # =========================================================================
    # Tuning Operations
    # =========================================================================

    def create_tuned_model(
        self,
        source_model: str,
        training_data: Any,
        display_name: str | None = None,
        epochs: int | None = None,
    ) -> dict[str, Any]:
        """Create a fine-tuned model."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            job = self.client.tunings.tune(
                base_model=source_model,
                training_data=training_data,
                config=types.CreateTunedModelConfig(
                    display_name=display_name, epoch_count=epochs
                ),
            )
            return job.model_dump()
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to create tuned model: %s", e)
            raise GeminiError(f"Failed to create tuned model: {e}") from e

    def list_tuned_models(self) -> list[dict[str, Any]]:
        """list all tuned models."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return [m.model_dump() for m in self.client.tunings.list()]
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to list tuned models: %s", e)
            raise GeminiError(f"Failed to list tuned models: {e}") from e

    def get_tuned_model(self, name: str) -> dict[str, Any]:
        """Get a tuned model by name."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return self.client.tunings.get(name=name).model_dump()
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to get tuned model %s: %s", name, e)
            raise GeminiError(f"Failed to get tuned model {name}: {e}") from e

    def delete_tuned_model(self, name: str) -> bool:
        """Delete a tuned model."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            self.client.tunings.delete(name=name)
            return True
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to delete tuned model %s: %s", name, e)
            raise GeminiError(f"Failed to delete tuned model {name}: {e}") from e

    # =========================================================================
    # Batch Operations
    # =========================================================================

    def create_batch(
        self, requests: list[Any], model: str | None = None
    ) -> dict[str, Any]:
        """Create a batch inference job."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return self.client.batches.create(
                model=model or self.default_model,
                src=requests,
            ).model_dump()
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to create batch: %s", e)
            raise GeminiError(f"Failed to create batch: {e}") from e

    def get_batch(self, name: str) -> dict[str, Any]:
        """Get batch job status."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return self.client.batches.get(name=name).model_dump()
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to get batch %s: %s", name, e)
            raise GeminiError(f"Failed to get batch {name}: {e}") from e

    def list_batches(self) -> list[dict[str, Any]]:
        """list all batch jobs."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return [b.model_dump() for b in self.client.batches.list()]
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to list batches: %s", e)
            raise GeminiError(f"Failed to list batches: {e}") from e

    def delete_batch(self, name: str) -> bool:
        """Delete a batch job."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            self.client.batches.delete(name=name)
            return True
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to delete batch %s: %s", name, e)
            raise GeminiError(f"Failed to delete batch {name}: {e}") from e
