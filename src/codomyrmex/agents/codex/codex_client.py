"""OpenAI Codex API client."""

import time
from typing import Any, Iterator, Optional

try:
    import openai
except ImportError:
    openai = None

from codomyrmex.agents.config import get_config
from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
)
from codomyrmex.agents.exceptions import CodexError
from codomyrmex.agents.generic import BaseAgent


class CodexClient(BaseAgent):
    """Client for interacting with OpenAI Codex API."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize Codex client.

        Args:
            config: Optional configuration override
        """
        if openai is None:
            raise CodexError(
                "openai package not installed. Install with: pip install openai"
            )

        agent_config = get_config()
        super().__init__(
            name="codex",
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_EDITING,
                AgentCapabilities.CODE_ANALYSIS,
                AgentCapabilities.TEXT_COMPLETION,
                AgentCapabilities.STREAMING,
            ],
            config=config or {},
        )

        api_key = (
            config.get("codex_api_key")
            if config
            else agent_config.codex_api_key
        )
        if not api_key:
            raise CodexError("Codex API key not configured")

        self.model = (
            config.get("codex_model") if config else agent_config.codex_model
        )
        self.timeout = (
            config.get("codex_timeout") if config else agent_config.codex_timeout
        )
        self.max_tokens = (
            config.get("codex_max_tokens")
            if config
            else agent_config.codex_max_tokens
        )
        self.temperature = (
            config.get("codex_temperature")
            if config
            else agent_config.codex_temperature
        )

        self.client = openai.OpenAI(api_key=api_key)

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """
        Execute Codex API request.

        Args:
            request: Agent request

        Returns:
            Agent response
        """
        start_time = time.time()

        try:
            # Build prompt
            prompt = self._build_prompt(request)

            self.logger.debug(
                "Executing Codex API request",
                extra={
                    "agent": "codex",
                    "model": self.model,
                    "prompt_length": len(prompt),
                },
            )

            # Call Codex API
            response = self.client.completions.create(
                model=self.model,
                prompt=prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=self.timeout,
            )

            execution_time = time.time() - start_time

            # Extract content
            content = response.choices[0].text if response.choices else ""
            tokens_used = response.usage.prompt_tokens + response.usage.completion_tokens
            finish_reason = (
                response.choices[0].finish_reason if response.choices else None
            )

            self.logger.info(
                "Codex API request completed",
                extra={
                    "agent": "codex",
                    "model": self.model,
                    "execution_time": execution_time,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": tokens_used,
                    "content_length": len(content),
                    "finish_reason": finish_reason,
                },
            )

            return AgentResponse(
                content=content,
                metadata={
                    "model": self.model,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                    },
                    "finish_reason": finish_reason,
                },
                tokens_used=tokens_used,
                execution_time=execution_time,
            )

        except openai.APIError as e:
            execution_time = time.time() - start_time
            status_code = getattr(e, "status_code", None)
            self.logger.error(
                "Codex API error",
                exc_info=True,
                extra={
                    "agent": "codex",
                    "model": self.model,
                    "error": str(e),
                    "status_code": status_code,
                    "execution_time": execution_time,
                },
            )
            raise CodexError(
                f"Codex API error: {str(e)}",
                api_error=str(e),
                status_code=status_code,
            ) from e
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(
                "Unexpected error in Codex API request",
                exc_info=True,
                extra={
                    "agent": "codex",
                    "model": self.model,
                    "error": str(e),
                    "execution_time": execution_time,
                },
            )
            raise CodexError(
                f"Unexpected error: {str(e)}",
                api_error=str(e),
            ) from e

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """
        Stream Codex API response.

        Args:
            request: Agent request

        Yields:
            Chunks of response content
        """
        try:
            prompt = self._build_prompt(request)

            self.logger.debug(
                "Starting Codex API stream",
                extra={
                    "agent": "codex",
                    "model": self.model,
                    "prompt_length": len(prompt),
                },
            )

            chunk_count = 0
            stream = self.client.completions.create(
                model=self.model,
                prompt=prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=self.timeout,
                stream=True,
            )

            for chunk in stream:
                if chunk.choices:
                    content = chunk.choices[0].text
                    if content:
                        chunk_count += 1
                        yield content

            self.logger.debug(
                "Codex API stream completed",
                extra={
                    "agent": "codex",
                    "model": self.model,
                    "chunk_count": chunk_count,
                },
            )

        except openai.APIError as e:
            self.logger.error(
                "Codex API streaming error",
                exc_info=True,
                extra={
                    "agent": "codex",
                    "model": self.model,
                    "error": str(e),
                },
            )
            yield f"Error: Codex API error: {str(e)}"
        except Exception as e:
            self.logger.error(
                "Unexpected error in Codex API stream",
                exc_info=True,
                extra={
                    "agent": "codex",
                    "model": self.model,
                    "error": str(e),
                },
            )
            yield f"Error: {str(e)}"

    def _build_prompt(self, request: AgentRequest) -> str:
        """
        Build Codex prompt from request.

        Args:
            request: Agent request

        Returns:
            Prompt string
        """
        prompt = request.prompt

        # Add context if provided
        if request.context:
            context_str = "\n".join(
                f"{k}: {v}" for k, v in request.context.items()
            )
            prompt = f"{context_str}\n\n{prompt}"

        return prompt

