"""Perplexity API integration for Codomyrmex.

Implements `APIAgentBase` to interface with Perplexity's chat completions API
(https://api.perplexity.ai/chat/completions) providing real-time search capabilities.
"""

from __future__ import annotations

import json
import os
import time
from typing import TYPE_CHECKING, Any

import requests

from codomyrmex.agents.core import AgentRequest, AgentResponse
from codomyrmex.agents.core.exceptions import AgentError
from codomyrmex.agents.generic import APIAgentBase

if TYPE_CHECKING:
    import collections.abc


class PerplexityError(AgentError):
    """Exception raised by the Perplexity API client."""


class PerplexityClient(APIAgentBase):
    """Client for Perplexity's online search-augmented LLMs."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the Perplexity client.

        Args:
            config: Optional override dict containing:
                - perplexity_api_key: Perplexity API key
                - timeout: Request timeout
        """
        import requests

        from codomyrmex.agents.core import AgentCapabilities

        super().__init__(
            name="perplexity",
            capabilities=[
                AgentCapabilities.TEXT_COMPLETION,
                AgentCapabilities.STREAMING,
                AgentCapabilities.MULTI_TURN,
            ],
            api_key_config_key="perplexity_api_key",
            model_config_key="perplexity_model",
            timeout_config_key="perplexity_timeout",
            max_tokens_config_key="perplexity_max_tokens",
            temperature_config_key="perplexity_temperature",
            client_class=requests.Session,
            client_init_func=lambda key: requests.Session(),
            error_class=PerplexityError,
            config=config,
        )
        self.api_key = self._extract_config_value(
            "perplexity_api_key",
            default=os.environ.get("PERPLEXITY_API_KEY"),
            config=config,
        )
        self.timeout = self._extract_config_value(
            "perplexity_timeout", default=120, config=config
        )
        self.api_base = "https://api.perplexity.ai/chat/completions"
        self.default_model = "sonar"

    def test_connection(self) -> bool:
        """Verify API key configuration and basic connectedness.

        Returns:
            bool: True if minimally configured.
        """
        return bool(self.api_key)

    def execute(self, request: AgentRequest, max_tokens: int | None = None) -> AgentResponse:
        """Execute a single-turn completion against Perplexity.

        Args:
            request: The standard AgentRequest object containing prompt and contexts.
            max_tokens: Optional maximum tokens for the response.

        Returns:
            AgentResponse: Structured response encapsulation.
        """
        if not self.api_key:
            return AgentResponse(
                content="",
                error="PERPLEXITY_API_KEY environment variable is missing or empty.",
                metadata={"agent": self.name},
            )

        model = request.context.get("model", self.default_model)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Structure payload
        messages = request.context.get("messages", [])
        if not messages:
            messages = [{"role": "user", "content": request.prompt}]

        payload = {
            "model": model,
            "messages": messages,
        }

        # Optional search parameters / standard completion parameters
        if request.context and "temperature" in request.context:
            payload["temperature"] = request.context["temperature"]
        if request.context and "max_tokens" in request.context:
            payload["max_tokens"] = request.context["max_tokens"]

        start_time = time.time()
        try:
            response = requests.post(
                self.api_base,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = data.get("usage", {})

            return AgentResponse(
                content=str(content),
                metadata={
                    "agent": self.name,
                    "model": model,
                    "citations": data.get("citations", []),
                },
                tokens_used=usage.get("total_tokens", 0),
                execution_time=time.time() - start_time,
            )

        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_json = e.response.json()
                    error_msg = f"{e}: {error_json}"
                except ValueError:
                    error_msg = f"{e}: {e.response.text}"
            return AgentResponse(
                content="",
                error=f"Perplexity API execution failed: {error_msg}",
                metadata={"agent": self.name},
                execution_time=time.time() - start_time,
            )

    def stream(self, request: AgentRequest) -> collections.abc.Iterator[str]:
        """Stream a response from Perplexity.

        Args:
            request: AgentRequest containing prompt/messages.

        Yields:
            str: Token chunks from the API.
        """
        if not self.api_key:
            yield "Error: PERPLEXITY_API_KEY environment variable is missing or empty."
            return

        model = request.context.get("model", self.default_model)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }

        messages = request.context.get("messages", [])
        if not messages:
            messages = [{"role": "user", "content": request.prompt}]

        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
        }

        if request.context and "temperature" in request.context:
            payload["temperature"] = request.context["temperature"]
        if request.context and "max_tokens" in request.context:
            payload["max_tokens"] = request.context["max_tokens"]

        try:
            with requests.post(
                self.api_base,
                headers=headers,
                json=payload,
                timeout=self.timeout,
                stream=True,
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode("utf-8")
                        if line_str.startswith("data: "):
                            data_str = line_str[6:]
                            if data_str.strip() == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data_str)
                                content = (
                                    chunk.get("choices", [{}])[0]
                                    .get("delta", {})
                                    .get("content", "")
                                )
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                pass

        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            yield f"\n[Stream Error: {error_msg}]"
