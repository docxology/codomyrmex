from typing import Any, Iterator, Optional
import time

import openai

from codomyrmex.agents.config import get_config
from codomyrmex.agents.core import (
from codomyrmex.agents.exceptions import CodexError
from codomyrmex.agents.generic.api_agent_base import APIAgentBase
from codomyrmex.logging_monitoring import get_logger












































    openai = None

    AgentCapabilities,
    AgentRequest,
    AgentResponse,
)
try:
except ImportError:


class CodexClient(APIAgentBase):
    """Client for interacting with OpenAI Codex API."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize Codex client.

        Args:
            config: Optional configuration override
        """
        super().__init__(
            name="codex",
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_EDITING,
                AgentCapabilities.CODE_ANALYSIS,
                AgentCapabilities.TEXT_COMPLETION,
                AgentCapabilities.STREAMING,
            ],
            api_key_config_key="codex_api_key",
            model_config_key="codex_model",
            timeout_config_key="codex_timeout",
            max_tokens_config_key="codex_max_tokens",
            temperature_config_key="codex_temperature",
            client_class=openai,
            client_init_func=lambda api_key: openai.OpenAI(api_key=api_key),
            error_class=CodexError,
            config=config,
        )

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
            
            # Extract tokens using base class helper
            input_tokens, output_tokens = self._extract_tokens_from_response(
                response, "openai"
            )
            tokens_used = input_tokens + output_tokens
            finish_reason = (
                response.choices[0].finish_reason if response.choices else None
            )

            self.logger.info(
                "Codex API request completed",
                extra={
                    "agent": "codex",
                    "model": self.model,
                    "execution_time": execution_time,
                    "prompt_tokens": input_tokens,
                    "completion_tokens": output_tokens,
                    "total_tokens": tokens_used,
                    "content_length": len(content),
                    "finish_reason": finish_reason,
                },
            )

            return self._build_agent_response(
                content=content,
                metadata={
                    "usage": {
                        "prompt_tokens": input_tokens,
                        "completion_tokens": output_tokens,
                    },
                    "finish_reason": finish_reason,
                },
                tokens_used=tokens_used,
                execution_time=execution_time,
            )

        except openai.APIError as e:
            execution_time = time.time() - start_time
            self._handle_api_error(e, execution_time, openai.APIError)
        except Exception as e:
            execution_time = time.time() - start_time
            self._handle_api_error(e, execution_time)

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
            context_str = "\\n".join(
                f"{k}: {v}" for k, v in request.context.items()
            )
            prompt = f"{context_str}\\n\\n{prompt}"

        return prompt
