"""Claude API client for Codomyrmex agents.

Provides a robust, feature-rich client for interacting with Anthropic's Claude API
with support for:
- System messages and multi-turn conversations
- Streaming responses
- Tool/function calling
- Code intelligence (editing, reviewing, explaining)
- Command execution and project scanning
"""

from __future__ import annotations

from typing import Any

from codomyrmex.agents.core import (
    AgentCapabilities,
)
from codomyrmex.agents.core.exceptions import ClaudeError
from codomyrmex.agents.core.session import SessionManager
from codomyrmex.agents.generic.api_agent_base import APIAgentBase
from codomyrmex.logging_monitoring.core.logger_config import get_logger

from .mixins.code_intel import CodeIntelMixin
from .mixins.execution import ExecutionMixin
from .mixins.file_ops import FileOpsMixin
from .mixins.session import SessionMixin
from .mixins.system_ops import SystemOpsMixin
from .mixins.tools import ToolsMixin

try:
    import anthropic
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
except ImportError:
    anthropic = None
    MessageCreateParamsNonStreaming = dict

logger = get_logger(__name__)

CLAUDE_PRICING = {
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    "claude-3-5-haiku-20241022": {"input": 1.00, "output": 5.00},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-opus-4-5-20251101": {"input": 15.00, "output": 75.00},
}

DEFAULT_CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
MAX_RETRIES = 3
BASE_BACKOFF = 2.0


class ClaudeClient(
    ExecutionMixin,
    ToolsMixin,
    SessionMixin,
    FileOpsMixin,
    CodeIntelMixin,
    SystemOpsMixin,
    APIAgentBase,
):
    """Client for interacting with Claude API.

    A comprehensive client that wraps the Anthropic API with:
    - Proper system message support
    - Retry logic with exponential backoff for transient failures
    - Tool/function calling capabilities
    - Session management for multi-turn conversations
    - Cost estimation based on token usage
    - Streaming support with metadata tracking
    """

    # Default retry configuration
    DEFAULT_MAX_RETRIES = 3

    DEFAULT_INITIAL_DELAY = 1.0

    DEFAULT_MAX_DELAY = 60.0

    DEFAULT_BACKOFF_FACTOR = 2.0

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        session_manager: SessionManager | None = None,
    ):
        """Initialize Claude client.

        Args:
            config: Optional configuration override. Supported keys:
                - claude_api_key: API key (or from ANTHROPIC_API_KEY env)
                - claude_model: Model to use (default: claude-3-5-sonnet-20241022)
                - claude_timeout: Request timeout in seconds
                - claude_max_tokens: Maximum output tokens
                - claude_temperature: Sampling temperature
                - max_retries: Maximum retry attempts for transient failures
                - initial_retry_delay: Initial delay between retries
            session_manager: Optional session manager for multi-turn conversations
        """
        super().__init__(
            name="claude",
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_EDITING,
                AgentCapabilities.CODE_ANALYSIS,
                AgentCapabilities.TEXT_COMPLETION,
                AgentCapabilities.STREAMING,
                AgentCapabilities.MULTI_TURN,
                AgentCapabilities.TOOL_USE,
                AgentCapabilities.VISION,
                AgentCapabilities.CACHING,
            ],
            api_key_config_key="claude_api_key",
            model_config_key="claude_model",
            timeout_config_key="claude_timeout",
            max_tokens_config_key="claude_max_tokens",
            temperature_config_key="claude_temperature",
            client_class=anthropic,
            client_init_func=lambda api_key: anthropic.Anthropic(api_key=api_key),
            error_class=ClaudeError,
            config=config,
        )

        # Retry configuration
        self.max_retries = (config or {}).get("max_retries", self.DEFAULT_MAX_RETRIES)
        self.initial_retry_delay = (config or {}).get(
            "initial_retry_delay", self.DEFAULT_INITIAL_DELAY
        )
        self.max_retry_delay = (config or {}).get(
            "max_retry_delay", self.DEFAULT_MAX_DELAY
        )
        self.backoff_factor = (config or {}).get(
            "backoff_factor", self.DEFAULT_BACKOFF_FACTOR
        )

        # Session management
        self.session_manager = session_manager

        # Registered tools for function calling
        self._tools: list[dict[str, Any]] = []

