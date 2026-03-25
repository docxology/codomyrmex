"""Unified LLM Client for Real Agent Integration.

Provides a factory to get a real LLM client (Claude or Ollama) for use in
autonomous agents, CLI tools, and skills.
"""

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any

from codomyrmex.agents.core.base import AgentRequest, AgentResponse
from codomyrmex.config_management.defaults import DEFAULT_OLLAMA_URL
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

_OLLAMA_ALLOWED_PREFIXES = (
    "http://localhost:",
    "http://127.0.0.1:",
    "https://localhost:",
    "https://127.0.0.1:",
)


class OllamaClient:
    """Client for local Ollama instance (REST API).

    Implements a robust interface compatible with ClaudeClient
    for use in ClaudeCodeEndpoint, using real LLM inference.
    """

    def __init__(self, model: str = "llama3", base_url: str = DEFAULT_OLLAMA_URL):
        if not any(base_url.startswith(prefix) for prefix in _OLLAMA_ALLOWED_PREFIXES):
            raise ValueError(
                f"base_url must be a localhost address to prevent SSRF: {base_url!r}"
            )
        self.model = model
        self.base_url = base_url
        self.session_manager = None  # dummy for interface compatibility

    def create_session(self, session_id: str) -> None:
        raise NotImplementedError("LLM session management not implemented")

    def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute request using Ollama."""
        return self.execute_with_session(request)

    def _call_ollama(self, url: str, payload: dict) -> tuple[str, str | None]:
        """POST payload to Ollama and return (content, error)."""
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=120.0) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    return data.get("message", {}).get("content", ""), None
                return "", f"Ollama returned {response.status}"
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            try:
                with urllib.request.urlopen(
                    f"{self.base_url}/api/tags", timeout=1.0
                ) as resp:
                    if resp.status == 200:
                        tags = json.loads(resp.read().decode("utf-8"))
                        models = [m.get("name") for m in tags.get("models", [])]
                        logger.debug("Available models for debugging: %s", models)
            except (
                ValueError,
                RuntimeError,
                AttributeError,
                OSError,
                TypeError,
            ) as debug_err:
                logger.debug(
                    "Failed to list available Ollama models for debug: %s", debug_err
                )
            return "", f"Real Ollama Connection Failed: {e}"

    def execute_with_session(
        self, request: AgentRequest, session: Any = None, session_id: Any = None
    ) -> AgentResponse:
        """Execute request using Ollama /api/chat for real conversation."""
        url = f"{self.base_url}/api/chat"
        # Build structured messages (no string splitting — prevents prompt injection)
        messages = []
        if request.metadata and request.metadata.get("system"):
            messages.append({"role": "system", "content": request.metadata["system"]})
        messages.append({"role": "user", "content": request.prompt})
        payload = {"model": self.model, "messages": messages, "stream": False}
        start_time = time.monotonic()
        content, error = self._call_ollama(url, payload)
        elapsed = time.monotonic() - start_time
        return AgentResponse(
            content=content,
            error=error,
            tokens_used=0,
            execution_time=elapsed,
            metadata={"model": self.model, "provider": "ollama"},
        )


def get_llm_client(identity: str = "agent") -> Any:
    """Factory to get the best available REAL LLM client.

    Priority:
    1. ClaudeClient (if ANTHROPIC_API_KEY set)
    2. GeminiClient (if GEMINI_API_KEY set)
    3. O1Client (if OPENAI_API_KEY set)
    4. DeepSeekClient (if DEEPSEEK_API_KEY set)
    5. OllamaClient (if reachable)

    Raises RuntimeError if no real client is available.
    """
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            from codomyrmex.agents.claude.claude_client import ClaudeClient

            logger.info("[%s] Using real ClaudeClient (API Key found)", identity)
            return ClaudeClient()
        except ImportError as e:
            logger.warning("[%s] ClaudeClient import failed: %s", identity, e)

    if os.environ.get("GEMINI_API_KEY"):
        try:
            from codomyrmex.agents.gemini.gemini_client import GeminiClient

            logger.info("[%s] Using real GeminiClient (API Key found)", identity)
            return GeminiClient()
        except ImportError as e:
            logger.warning("[%s] GeminiClient import failed: %s", identity, e)

    # 3. Check O1
    if os.environ.get("OPENAI_API_KEY"):
        try:
            from codomyrmex.agents.o1.o1_client import O1Client

            logger.info("[%s] Using real O1Client (API Key found)", identity)
            return O1Client()
        except ImportError as e:
            logger.warning("[%s] O1Client import failed: %s", identity, e)

    # 4. Check DeepSeek
    if os.environ.get("DEEPSEEK_API_KEY"):
        try:
            from codomyrmex.agents.deepseek.deepseek_client import DeepSeekClient

            logger.info("[%s] Using real DeepSeekClient (API Key found)", identity)
            return DeepSeekClient()
        except ImportError as e:
            logger.warning("[%s] DeepSeekClient import failed: %s", identity, e)

    # 5. Check Ollama
    try:
        # Quick health check
        base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        with urllib.request.urlopen(f"{base}/api/tags", timeout=1.0) as resp:
            if resp.status == 200:
                # Use configured model or default
                model = os.environ.get("OLLAMA_MODEL", "codellama:latest")
                logger.info(
                    "[%s] Using real OllamaClient (Localhost reachable, model=%s)",
                    identity,
                    model,
                )
                return OllamaClient(model=model)
    except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
        logger.warning("[%s] Ollama connection check failed: %s", identity, e)

    raise RuntimeError(
        f"[{identity}] CRITICAL: No Real LLM Available.\n"
        "Please set ANTHROPIC_API_KEY for Claude,\n"
        "OR GEMINI_API_KEY for Gemini,\n"
        "OR OPENAI_API_KEY for O1,\n"
        "OR DEEPSEEK_API_KEY for DeepSeek,\n"
        "OR ensure Ollama is running at http://localhost:11434.\n"
        "Mocks are strictly forbidden."
    )


__all__ = [
    "AgentRequest",
    "AgentResponse",
    "OllamaClient",
    "get_llm_client",
]
