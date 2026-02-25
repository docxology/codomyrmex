"""AI Code Editing Configuration & Setup."""

import os
from typing import Any

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None
try:
    from google import genai
except ImportError:
    genai = None

try:
    from codomyrmex.llm.providers.ollama_manager import OLLAMA_AVAILABLE, OllamaManager
except ImportError:
    OllamaManager = None
    OLLAMA_AVAILABLE = False

try:
    from codomyrmex.performance import monitor_performance
except ImportError:
    def monitor_performance(name):
        def decorator(func):
            return func
        return decorator


from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

# Default LLM configurations
DEFAULT_LLM_PROVIDER = "google"

DEFAULT_LLM_MODEL = {
    "openai": "gpt-3.5-turbo",
    "anthropic": "claude-instant-1",
    "google": "gemini-flash-latest",
    "ollama": "llama3.1:latest",
}

# Retry configuration for API calls
MAX_RETRIES = 3

RETRY_DELAY = 1.0  # seconds

# LLM client initialization
@monitor_performance("llm_client_initialization")
def get_llm_client(provider: str, model_name: str | None = None) -> tuple[Any, str]:
    """
    Initialize and return an LLM client based on the specified provider.

    Args:
        provider: The LLM provider to use (e.g., "openai", "anthropic")
        model_name: Optional specific model to use

    Returns:
        Tuple of (client, model_name)

    Raises:
        ImportError: If the required client library is not installed
        ValueError: If the provider is not supported or configuration is invalid
    """
    provider = provider.lower()

    if provider == "openai":
        try:

            # Check for API key
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")

            client = OpenAI(api_key=api_key)
            model = model_name or DEFAULT_LLM_MODEL["openai"]
            return client, model

        except ImportError as e:
            raise ImportError(
                "OpenAI Python package not installed. Install with: pip install openai"
            ) from e

    elif provider == "anthropic":
        try:

            # Check for API key
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")

            client = Anthropic(api_key=api_key)
            model = model_name or DEFAULT_LLM_MODEL["anthropic"]
            return client, model

        except ImportError as e:
            raise ImportError(
                "Anthropic Python package not installed. Install with: pip install anthropic"
            ) from e

    elif provider == "google":
        try:
            # Check for API key (support both variations)
            api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("Neither GEMINI_API_KEY nor GOOGLE_API_KEY environment variable is set")

            client = genai.Client(api_key=api_key)
            model = model_name or DEFAULT_LLM_MODEL["google"]
            return client, model

        except (ImportError, ValueError, AttributeError, OSError) as e:
            raise RuntimeError(f"Failed to initialize Google Gemini client: {e}") from None

    elif provider == "ollama":
        if not OLLAMA_AVAILABLE:
            raise ImportError(
                "Ollama integration not available. Install with: pip install codomyrmex[ollama]"
            )
        try:
            manager = OllamaManager(auto_start_server=True)
            model = model_name or DEFAULT_LLM_MODEL["ollama"]
            return manager, model
        except (ImportError, OSError, ConnectionError, RuntimeError, ValueError) as e:
            raise RuntimeError(f"Failed to initialize Ollama client: {e}") from None

    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}. Supported providers: openai, anthropic, google, ollama"
        )

