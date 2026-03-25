"""Gemini API client via google-genai SDK.

The client is composed from focused mixin classes for maintainability:

- Core: ``__init__``, ``_execute_impl``, ``_stream_impl``, chat, content building
- ``GeminiMediaMixin`` — image generation/editing/upscaling, video generation
- ``GeminiFilesMixin`` — file upload/list/get/delete
- ``GeminiCacheMixin`` — cached content CRUD
- ``GeminiTuningBatchMixin`` — model tuning and batch inference
"""

import os
from collections.abc import Iterator
from typing import Any

from google import genai
from google.genai import types

try:
    from PIL import Image as PILImage
except ImportError:
    PILImage = None  # type: ignore[assignment]

# Image is the PIL Image module for use with Image.open() calls
Image: Any = PILImage

from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
    BaseAgent,
)
from codomyrmex.agents.core.exceptions import GeminiError
from codomyrmex.logging_monitoring import get_logger

from ._cache import GeminiCacheMixin
from ._files import GeminiFilesMixin
from ._media import GeminiMediaMixin
from ._tuning_batch import GeminiTuningBatchMixin

logger = get_logger(__name__)


class GeminiClient(
    GeminiMediaMixin,
    GeminiFilesMixin,
    GeminiCacheMixin,
    GeminiTuningBatchMixin,
    BaseAgent,
):
    """Client for interacting with Gemini API via google-genai SDK.

    All resource-management operations (media, files, cache, tuning, batch)
    are delegated to focused mixin classes for improved maintainability.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(
            name="gemini",
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_EDITING,
                AgentCapabilities.CODE_ANALYSIS,
                AgentCapabilities.TEXT_COMPLETION,
                AgentCapabilities.STREAMING,
                AgentCapabilities.MULTI_TURN,
                AgentCapabilities.VISION,
                AgentCapabilities.CODE_EXECUTION,
            ],
            config=config or {},
        )

        if genai is None:
            raise ImportError("google-genai package not found. Please install it.")

        self.use_vertex = self.get_config_value(
            "use_vertex_ai", default=False, config=config
        )
        self.vertex_project = self.get_config_value("vertex_project", config=config)
        self.vertex_location = self.get_config_value(
            "vertex_location", default="us-central1", config=config
        )

        self.api_key = self.get_config_value(
            "gemini_api_key", config=config
        ) or os.getenv("GEMINI_API_KEY")

        self.client = None

        try:
            if self.use_vertex:
                client_kwargs = {"vertexai": True}
                if self.vertex_project:
                    client_kwargs["project"] = self.vertex_project
                if self.vertex_location:
                    client_kwargs["location"] = self.vertex_location
                self.client = genai.Client(**client_kwargs)
                logger.debug("Initialized Gemini Client with Vertex AI")
            elif not self.api_key:
                logger.debug("No GEMINI_API_KEY found; client operations that need the API will fail until a key is set.")
            else:
                client_kwargs = {"api_key": self.api_key}
                self.client = genai.Client(**client_kwargs)
                logger.debug("Initialized Gemini Client with API Key")
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to initialize Gemini Client: %s", e)
            raise GeminiError(f"Failed to initialize Gemini Client: {e}") from e

        self.default_model = self.get_config_value(
            "gemini_model",
            default="gemini-2.5-flash",
            config=config,
        )

        self.max_retries = (config or {}).get("max_retries", 3)
        self.initial_retry_delay = (config or {}).get("initial_retry_delay", 1.0)
        self.max_retry_delay = (config or {}).get("max_retry_delay", 60.0)
        self.backoff_factor = (config or {}).get("backoff_factor", 2.0)

    # =========================================================================
    # Core Agent Interface
    # =========================================================================

    def _execute_impl(
        self, request: AgentRequest, max_tokens: int | None = None
    ) -> AgentResponse:
        """Execute Gemini API request."""
        import time

        if not self.client:
            raise GeminiError("Gemini Client not initialized")

        prompt = request.prompt
        context = request.context or {}
        model = context.get("model", self.default_model)

        config_params = {}

        if "response_schema" in context:
            config_params["response_mime_type"] = "application/json"
            config_params["response_schema"] = context["response_schema"]

        if "system_instruction" in context:
            config_params["system_instruction"] = context["system_instruction"]

        if "safety_settings" in context:
            config_params["safety_settings"] = context["safety_settings"]

        if "tools" in context:
            tools_config = []
            for tool in context["tools"]:
                if isinstance(tool, str):
                    if tool == "code_execution":
                        tools_config.append(
                            types.Tool(code_execution=types.CodeExecution())
                        )
                    elif tool == "google_search":
                        tools_config.append(
                            types.Tool(google_search=types.GoogleSearch())
                        )
                else:
                    tools_config.append(tool)
            config_params["tools"] = tools_config

        if "tool_config" in context:
            config_params["tool_config"] = context["tool_config"]

        if "cached_content" in context:
            config_params["cached_content"] = context["cached_content"]

        contents = self._build_contents(prompt, context)

        start_time = time.time()
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(**config_params)
                if config_params
                else None,
            )
            return self._build_response_from_api_result(response, request)
        except Exception as e:
            execution_time = time.time() - start_time
            return self._handle_gemini_error(e, execution_time, request.id)

    def _handle_gemini_error(
        self, error: Exception, execution_time: float, request_id: str | None = None
    ) -> AgentResponse:
        """Handle Gemini-specific API errors."""
        api_error_str = str(error)
        status_code = getattr(error, "code", None)

        self.logger.error(
            "Gemini API error",
            extra={
                "agent": "gemini",
                "error": api_error_str,
                "status_code": status_code,
                "execution_time": execution_time,
            },
        )

        try:
            raise GeminiError(
                f"Gemini API error: {api_error_str}",
                api_error=api_error_str,
                status_code=status_code,
            ) from error
        except GeminiError as e:
            return AgentResponse(
                content="",
                error=str(e),
                metadata={"error_type": type(e).__name__},
                request_id=request_id,
                execution_time=execution_time,
            )

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")

        prompt = request.prompt
        context = request.context or {}
        model = context.get("model", self.default_model)
        contents = self._build_contents(prompt, context)

        config_params = {}
        if "system_instruction" in context:
            config_params["system_instruction"] = context["system_instruction"]

        try:
            response_stream = self.client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(**config_params)
                if config_params
                else None,
            )
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Gemini streaming failed: %s", e)
            yield f"\n[Error: {e}]"

    def start_chat(
        self,
        history: list[dict[str, Any]] | None = None,
        enable_automatic_function_calling: bool = False,
        model: str | None = None,
    ) -> Any:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")

        model_name = model or self.default_model
        model_client = self.client.generative_model(model_name)

        return model_client.start_chat(
            history=history,
            enable_automatic_function_calling=enable_automatic_function_calling,
        )

    # =========================================================================
    # Model Metadata
    # =========================================================================

    def list_models(self) -> list[dict[str, Any]]:
        """list available Gemini models."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return [m.model_dump() for m in self.client.models.list()]
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to list models: %s", e)
            raise GeminiError(f"Failed to list models: {e}") from e

    def get_model(self, model_name: str) -> dict[str, Any]:
        """Get model metadata."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return self.client.models.get(model=model_name).model_dump()
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to get model %s: %s", model_name, e)
            raise GeminiError(f"Failed to get model {model_name}: {e}") from e

    def count_tokens(self, content: str | list[Any], model: str | None = None) -> int:
        """Count tokens in content."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            model_name = model or self.default_model
            resp = self.client.models.count_tokens(model=model_name, contents=content)
            return int(resp.total_tokens) if resp.total_tokens is not None else 0
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to count tokens: %s", e)
            raise GeminiError(f"Failed to count tokens: {e}") from e

    def embed_content(
        self, content: str | list[str], model: str = "text-embedding-004"
    ) -> list[list[float]]:
        """Generate embeddings for content."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            resp = self.client.models.embed_content(model=model, contents=content)
            if hasattr(resp, "embedding") and resp.embedding:
                return [list(resp.embedding.values or [])]
            if hasattr(resp, "embeddings") and resp.embeddings:
                return [list(e.values or []) for e in resp.embeddings]
            return []
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to embed content: %s", e)
            raise GeminiError(f"Failed to embed content: {e}") from e

    # =========================================================================
    # Internal Helpers
    # =========================================================================

    def _build_contents(self, prompt: str, context: dict[str, Any]) -> list[Any]:
        if "contents" in context:
            return context["contents"]

        parts = [prompt]
        if "images" in context:
            for img_path in context["images"]:
                try:
                    img = Image.open(img_path)
                    parts.append(img)
                except (OSError, AttributeError) as e:
                    logger.warning("Failed to load image: %s", e)
        return [parts]

    def _build_response_from_api_result(
        self, response: Any, request: AgentRequest
    ) -> AgentResponse:
        if not response.candidates:
            return AgentResponse(
                content="",
                error="No candidates returned",
                metadata={"raw": str(response)},
            )

        cand = response.candidates[0]
        content = ""

        if cand.content and cand.content.parts:
            for part in cand.content.parts:
                if part.text:
                    content += part.text
                if part.function_call:
                    content += f"\n[Function Call]: {part.function_call.name}({part.function_call.args})"
                if part.executable_code:
                    content += f"\n[Executable Code]:\n{part.executable_code.code}"
                if part.code_execution_result:
                    content += f"\n[Code Execution Result]: {part.code_execution_result.output}"

        return AgentResponse(
            request_id=request.id,
            content=content,
            metadata={
                "model": request.context.get("model", self.default_model),
                "finish_reason": str(cand.finish_reason),
                "usage": response.usage_metadata.model_dump()
                if response.usage_metadata
                else {},
            },
        )
