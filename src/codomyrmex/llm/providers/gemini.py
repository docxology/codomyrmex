"""Google Gemini LLM provider using the google-genai SDK.

Uses ``GEMINI_API_KEY`` (or ``GOOGLE_API_KEY``) for authentication.
Default model: ``gemini-2.5-pro`` (Gemini Ultra subscription tier).

Example::

    provider = get_provider(
        ProviderType.GOOGLE,
        api_key=os.environ["GEMINI_API_KEY"],
    )
    response = provider.complete(
        messages=[Message(role="user", content="Hello")],
    )
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from codomyrmex.llm.providers import (
    CompletionResponse,
    LLMProvider,
    Message,
    ProviderConfig,
    ProviderType,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

# Gemini models available via the google-genai SDK (Mar 2026)
GEMINI_MODELS = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
]


class GeminiProvider(LLMProvider):
    """Google Gemini provider via the ``google-genai`` SDK.

    Environment variable: ``GEMINI_API_KEY`` or ``GOOGLE_API_KEY``
    """

    provider_type = ProviderType.GOOGLE

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(config)
        if not self.config.api_key:
            self.config.api_key = os.getenv("GEMINI_API_KEY") or os.getenv(
                "GOOGLE_API_KEY"
            )
        self._init_client()

    def _init_client(self) -> None:
        """Initialize the google-genai client."""
        try:
            from google import genai

            self._client = genai.Client(api_key=self.config.api_key)
            self._genai_types = __import__("google.genai.types", fromlist=["types"])
        except ImportError:
            self._client = None
            self._genai_types = None

    # ---- completions -------------------------------------------------------

    def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> CompletionResponse:
        """Generate a completion from messages."""
        if not self._client:
            raise RuntimeError(
                "Gemini client not initialized. Install google-genai package."
            )

        model_name = self.get_model(model)
        contents = self._messages_to_contents(messages)

        config_params: dict[str, Any] = {"temperature": temperature}
        if max_tokens is not None:
            config_params["max_output_tokens"] = max_tokens

        # Extract system instruction from messages
        system_msgs = [m for m in messages if m.role == "system"]
        if system_msgs:
            config_params["system_instruction"] = system_msgs[0].content

        response = self._client.models.generate_content(
            model=model_name,
            contents=contents,
            config=self._genai_types.GenerateContentConfig(**config_params)
            if config_params
            else None,
            **kwargs,
        )

        content = ""
        if response.candidates and response.candidates[0].content:
            for part in response.candidates[0].content.parts:  # type: ignore
                if part.text:
                    content += part.text

        if response.usage_metadata:
            um = response.usage_metadata
            usage = {
                "prompt_tokens": getattr(um, "prompt_token_count", 0) or 0,
                "completion_tokens": getattr(um, "candidates_token_count", 0) or 0,
                "total_tokens": getattr(um, "total_token_count", 0) or 0,
            }

        return CompletionResponse(
            content=content,
            model=model_name,
            provider=self.provider_type,
            finish_reason=(
                str(response.candidates[0].finish_reason)
                if response.candidates
                else None
            ),
            usage=usage,
            raw_response=response,
        )

    def complete_stream(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        """Generate a streaming completion."""
        if not self._client:
            raise RuntimeError("Gemini client not initialized.")

        model_name = self.get_model(model)
        contents = self._messages_to_contents(messages)

        config_params: dict[str, Any] = {"temperature": temperature}
        if max_tokens is not None:
            config_params["max_output_tokens"] = max_tokens

        system_msgs = [m for m in messages if m.role == "system"]
        if system_msgs:
            config_params["system_instruction"] = system_msgs[0].content

        stream = self._client.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=self._genai_types.GenerateContentConfig(**config_params)
            if config_params
            else None,
            **kwargs,
        )

        for chunk in stream:
            if chunk.text:
                yield chunk.text

    async def complete_async(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> CompletionResponse:
        """Generate a completion asynchronously.

        Falls back to synchronous call (google-genai async support varies).
        """
        return self.complete(
            messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

    # ---- models ------------------------------------------------------------

    def list_models(self) -> list[str]:
        """List known Gemini models."""
        return list(GEMINI_MODELS)

    def _default_model(self) -> str:
        return "gemini-2.5-pro"

    # ---- helpers -----------------------------------------------------------

    @staticmethod
    def _messages_to_contents(messages: list[Message]) -> list[dict[str, Any]]:
        """Convert Message list to google-genai contents format.

        Filters out system messages (handled via ``system_instruction``).
        Maps ``assistant`` role to ``model`` as required by the Gemini API.
        """
        contents: list[dict[str, Any]] = []
        for msg in messages:
            if msg.role == "system":
                continue
            role = "model" if msg.role == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": msg.content}]})
        return contents
