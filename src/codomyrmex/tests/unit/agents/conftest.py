import asyncio
import json
import os
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Auto-detect OLLAMA_MODEL if not set — avoids skipping tests on machines
# that have Ollama running with models other than the default codellama:latest.
# ---------------------------------------------------------------------------
if not os.environ.get("OLLAMA_MODEL"):
    _base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        with urllib.request.urlopen(f"{_base}/api/tags", timeout=2) as _resp:
            _data = json.loads(_resp.read().decode())
            _models = sorted(m.get("name", "") for m in _data.get("models", []))
            if _models:
                os.environ["OLLAMA_MODEL"] = _models[0]  # smallest first
    except (urllib.error.URLError, OSError, TimeoutError, json.JSONDecodeError):
        pass

from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentError,
    AgentRequest,
    AgentResponse,
    BaseAgent,
    ToolRegistry,
)

# =============================================================================
# CONCRETE TEST IMPLEMENTATIONS (ZERO-MOCK COMPLIANCE)
# =============================================================================


class InMemoryLLMClient:
    """In-memory LLM client for test isolation.

    Records all calls and returns configurable responses.
    Uses real data structures — no mocking frameworks.
    """

    def __init__(self):
        self.chat_calls = []
        self.complete_calls = []
        self._chat_response = {"content": "Test response"}
        self._complete_response = "Test completion"

    def chat(self, *args, **kwargs):
        self.chat_calls.append((args, kwargs))
        return self._chat_response

    def complete(self, *args, **kwargs):
        self.complete_calls.append((args, kwargs))
        return self._complete_response

    def set_chat_response(self, response):
        self._chat_response = response

    def set_complete_response(self, response):
        self._complete_response = response


class ConcreteAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""

    def __init__(
        self,
        name: str = "test_agent",
        capabilities: list[AgentCapabilities] | None = None,
        config: dict[str, Any] | None = None,
    ):
        caps = capabilities or [
            AgentCapabilities.CODE_GENERATION,
            AgentCapabilities.TEXT_COMPLETION,
        ]
        super().__init__(name, caps, config)
        self._execute_called = False
        self._stream_called = False
        self._response = "Default test response"

    def set_response(self, response: str):
        """Set the response to return from execute."""
        self._response = response

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """Implementation of execute."""
        self._execute_called = True
        return AgentResponse(
            content=self._response,
            metadata={"agent": self.name},
            execution_time=0.1,
            tokens_used=10,
            request_id=request.id,
        )

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """Implementation of stream."""
        self._stream_called = True
        yield from self._response.split()


class FailingAgent(BaseAgent):
    """Agent that always fails for testing error handling."""

    def __init__(self, error_message: str = "Agent failed"):
        super().__init__("failing_agent", [AgentCapabilities.TEXT_COMPLETION])
        self._error_message = error_message

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        raise AgentError(self._error_message)

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        raise AgentError(self._error_message)


class AsyncAgent(BaseAgent):
    """Agent with async capabilities for testing."""

    def __init__(self, delay: float = 0.1):
        super().__init__(
            "async_agent",
            [AgentCapabilities.TEXT_COMPLETION, AgentCapabilities.STREAMING],
        )
        self._delay = delay

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        time.sleep(self._delay)
        return AgentResponse(
            content=f"Async response after {self._delay}s",
            metadata={"delay": self._delay},
        )

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        for i in range(3):
            time.sleep(self._delay / 3)
            yield f"Chunk {i + 1}"

    async def execute_async(self, request: AgentRequest) -> AgentResponse:
        """Async execution method."""
        await asyncio.sleep(self._delay)
        return AgentResponse(
            content=f"Async response after {self._delay}s",
            metadata={"async": True, "delay": self._delay},
        )


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def in_memory_llm_client():
    """Create an in-memory LLM client for testing."""
    return InMemoryLLMClient()


@pytest.fixture
def sample_agent_request():
    """Create a sample agent request for testing."""
    return AgentRequest(
        prompt="Test prompt",
        context={"key": "value"},
        capabilities=[AgentCapabilities.CODE_GENERATION],
        timeout=30,
        metadata={"test": True},
        id="test-request-123",
    )


@pytest.fixture
def temp_session_dir(tmp_path):
    """Create a temporary directory for session storage."""
    session_dir = tmp_path / "sessions"
    session_dir.mkdir()
    return session_dir


@pytest.fixture
def tool_registry():
    """Create a ToolRegistry with sample tools."""
    registry = ToolRegistry()

    def add_numbers(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    def greet(name: str) -> str:
        """Greet someone by name."""
        return f"Hello, {name}!"

    registry.register_function(add_numbers)
    registry.register_function(greet)
    return registry
