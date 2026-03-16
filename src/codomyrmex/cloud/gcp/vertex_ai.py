"""Google Cloud Vertex AI integration submodule."""

from typing import Any

from codomyrmex.logging_monitoring import get_logger

try:
    import vertexai
    from vertexai.generative_models import GenerationConfig, GenerativeModel
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False


logger = get_logger(__name__)


class VertexAIClient:
    """Wrapper for Google Cloud Vertex AI access."""

    def __init__(self, project: str | None = None, location: str = "us-central1"):
        """Initialize Vertex AI.

        Args:
            project: GCP Project ID. If None, uses application default credentials.
            location: GCP region (e.g., 'us-central1').
        """
        if not VERTEX_AI_AVAILABLE:
            logger.warning("Vertex AI SDK not installed. Please `pip install google-cloud-aiplatform`.")
            return

        self.project = project
        self.location = location

        try:
            vertexai.init(project=self.project, location=self.location)
            logger.debug(f"Vertex AI initialized for project {self.project} in {self.location}")
        except Exception as e:
            logger.error("Failed to initialize Vertex AI: %s", e)

    def is_available(self) -> bool:
        """Check if Vertex AI SDK is available and initialized."""
        return VERTEX_AI_AVAILABLE

    def get_generative_model(
        self,
        model_name: str = "gemini-1.5-pro-001",
        system_instruction: str | list[str] | None = None,
    ) -> Any:
        """Get a GenerativeModel instance for Gemini.

        Args:
            model_name: Name of the model.
            system_instruction: Optional system instructions.

        Returns:
            GenerativeModel instance or None if not available.
        """
        if not VERTEX_AI_AVAILABLE:
            raise RuntimeError("Vertex AI SDK not installed.")

        try:
            model = GenerativeModel(
                model_name=model_name,
                system_instruction=system_instruction,
            )
            return model
        except Exception as e:
            logger.error("Failed to get GenerativeModel %s: %s", model_name, e)
            return None

    def generate_content(
        self,
        model_name: str,
        contents: Any,
        generation_config: dict[str, Any] | None = None,
        system_instruction: str | list[str] | None = None,
    ) -> Any:
        """Generate content using Vertex AI.

        Args:
            model_name: Name of the model (e.g., 'gemini-1.5-pro-001').
            contents: Prompt content (string or list of parts).
            generation_config: Configuration dictionary (temperature, max_output_tokens, etc.).
            system_instruction: Optional system instruction.

        Returns:
            The generation response.
        """
        model = self.get_generative_model(
            model_name=model_name, system_instruction=system_instruction
        )
        if not model:
            raise RuntimeError("Failed to obtain GenerativeModel.")

        config = GenerationConfig(**generation_config) if generation_config else None

        try:
            response = model.generate_content(
                contents=contents,
                generation_config=config,
            )
            return response
        except Exception as e:
            logger.error("Vertex AI generate_content error: %s", e)
            raise
