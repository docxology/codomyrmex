"""
Model Runner - Flexible model execution for Codomyrmex

Provides advanced model execution capabilities with various parameters,
streaming support, and integration options.
"""

from dataclasses import dataclass

from codomyrmex.logging_monitoring import get_logger

from ._async_execution import OllamaAsyncExecutionMixin
from ._evaluation import OllamaEvaluationMixin
from ._execution import OllamaExecutionMixin
from .ollama_manager import OllamaManager


@dataclass
class ExecutionOptions:
    """
    Configuration options for model execution.

    All parameters are modular and can be set independently.
    Defaults are optimized for general-purpose text generation.

    Parameter Translation to Ollama API:
        This class uses standard LLM parameter names. When sent to Ollama,
        they are translated as follows:

        | Standard Name    | Ollama API Parameter |
        |------------------|---------------------|
        | max_tokens       | num_predict         |
        | context_window   | num_ctx             |
        | system_prompt    | system (at request level) |
        | temperature      | temperature         |
        | top_p            | top_p               |
        | top_k            | top_k               |
        | repeat_penalty   | repeat_penalty      |

    Parameters:
        temperature (float): Controls randomness (0.0-2.0). Lower = more deterministic.
            Default: 0.7
        top_p (float): Nucleus sampling threshold (0.0-1.0). Controls diversity.
            Default: 0.9
        top_k (int): Top-k sampling. Number of highest probability tokens to consider.
            Default: 40
        repeat_penalty (float): Penalty for repeating tokens (1.0 = no penalty).
            Default: 1.1
        max_tokens (int): Maximum number of tokens to generate.
            Maps to Ollama's `num_predict` parameter.
            Default: 2048
        timeout (int): Execution timeout in seconds.
            Default: 300
        stream (bool): Whether to stream the response (not yet fully implemented).
            Default: False
        format (Optional[str]): Output format, e.g., "json" for structured output.
            Default: None (text)
        system_prompt (Optional[str]): System prompt for the model.
            Maps to Ollama's `system` parameter at request level.
            Default: None
        context_window (Optional[int]): Context window size (if supported by model).
            Maps to Ollama's `num_ctx` parameter.
            Default: None
    """

    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    max_tokens: int = 2048
    timeout: int = 300
    stream: bool = False
    format: str | None = None  # "json" for structured output
    system_prompt: str | None = None
    context_window: int | None = None


@dataclass
class StreamingChunk:
    """A chunk of streaming response."""

    content: str
    done: bool = False
    token_count: int | None = None


class ModelRunner(OllamaExecutionMixin, OllamaAsyncExecutionMixin, OllamaEvaluationMixin):
    """
    Advanced model execution engine for Codomyrmex.

    Provides flexible execution with streaming, custom parameters,
    and integration with Codomyrmex ecosystem.
    """

    def __init__(self, ollama_manager: OllamaManager):
        """
        Initialize the model runner.

        Args:
            ollama_manager: Instance of OllamaManager
        """
        self.ollama_manager = ollama_manager
        self.logger = get_logger(__name__)
