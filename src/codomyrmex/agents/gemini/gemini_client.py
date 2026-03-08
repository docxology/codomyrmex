import os
from collections.abc import Iterator
from typing import Any

from google import genai
from google.genai import types
from PIL import Image

from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
    BaseAgent,
)
from codomyrmex.agents.core.exceptions import GeminiError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class GeminiClient(BaseAgent):
    """Client for interacting with Gemini API via google-genai SDK."""

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

        self.api_key = self.get_config_value(
            "gemini_api_key", config=config
        ) or os.getenv("GEMINI_API_KEY")
        self.client = None
        if not self.api_key:
            logger.warning("No GEMINI_API_KEY found. Some operations will fail.")
        else:
            try:
                # Use http_options with retry configuration if available in the SDK
                # Some versions might use different parameters, so we handle it gracefully
                client_kwargs = {"api_key": self.api_key}
                (config or {}).get("max_retries", 3)

                # Rely on default google-genai SDK timeout/retry behavior
                # for v1.0+ compatibility instead of injecting HttpOptions

                self.client = genai.Client(**client_kwargs)
            except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
                logger.error("Failed to initialize Gemini Client: %s", e)
                raise GeminiError(f"Failed to initialize Gemini Client: {e}") from e

        self.default_model = self.get_config_value(
            "gemini_model", default="gemini-3.1-pro-preview", config=config
        )

        # Retry configuration
        self.max_retries = (config or {}).get("max_retries", 3)
        self.initial_retry_delay = (config or {}).get("initial_retry_delay", 1.0)
        self.max_retry_delay = (config or {}).get("max_retry_delay", 60.0)
        self.backoff_factor = (config or {}).get("backoff_factor", 2.0)

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
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
            import time
            execution_time = time.time() - start_time
            # For Gemini google-genai SDK, we use a generic Exception check
            # or could use google.api_core.exceptions if we had it imported.
            # Base class _handle_api_error will wrap it in GeminiError.
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

    def list_models(self) -> list[dict[str, Any]]:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return [m.model_dump() for m in self.client.models.list()]
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to list models: %s", e)
            raise GeminiError(f"Failed to list models: {e}") from e

    def get_model(self, model_name: str) -> dict[str, Any]:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return self.client.models.get(model=model_name).model_dump()
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to get model %s: %s", model_name, e)
            raise GeminiError(f"Failed to get model {model_name}: {e}") from e

    def count_tokens(self, content: str | list[Any], model: str | None = None) -> int:
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

    def generate_images(
        self, prompt: str, model: str = "imagen-4.0-generate-001", **kwargs: Any
    ) -> list[dict[str, Any]]:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            config = kwargs.pop("config", None)
            if config is None and kwargs:
                config = kwargs

            result = self.client.models.generate_images(
                model=model, prompt=prompt, config=config
            )
            # Bypass Pydantic internals to prevent 'KeyboardInterrupt' resolution hangs
            return [{"image_bytes": img.image_bytes} for img in result.images]
        except Exception as e:
            logger.error("Failed to generate images: %s", e)
            raise GeminiError(f"Failed to generate images: {e}") from e

    def upscale_image(
        self,
        image: Any,
        upscale_factor: str = "x4",
        model: str = "imagen-latest",
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            config = kwargs.pop("config", None)
            if config is None and kwargs:
                config = kwargs

            result = self.client.models.upscale_image(
                model=model,
                image=image,
                upscale_factor=upscale_factor,
                config=config,
            )
            return [img.model_dump() for img in result.images]
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to upscale image: %s", e)
            raise GeminiError(f"Failed to upscale image: {e}") from e

    def edit_image(
        self,
        prompt: str,
        image: Any,
        reference_images: list[Any] | None = None,
        model: str = "imagen-latest",
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            config = kwargs.pop("config", None)
            if config is None and kwargs:
                config = kwargs

            # The SDK might expect reference_images instead of a single image
            # Or both. If image is provided, we use it or wrap it.
            ref_images = reference_images or []
            if image and not ref_images:
                ref_images = [image]

            result = self.client.models.edit_image(
                model=model,
                prompt=prompt,
                reference_images=ref_images,
                config=config,
            )
            return [img.model_dump() for img in result.images]
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to edit image: %s", e)
            raise GeminiError(f"Failed to edit image: {e}") from e

    def generate_videos(
        self, prompt: str, model: str = "veo-2.0-generate-001", **kwargs: Any
    ) -> list[dict[str, Any]]:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            config = kwargs.pop("config", None)
            if config is None and kwargs:
                config = kwargs

            operation = self.client.models.generate_videos(
                model=model, prompt=prompt, config=config
            )

            # Veo 2.0 returns a LongRunning Operation that requires polling
            if hasattr(operation, "done"):
                import time

                while not operation.done:
                    time.sleep(5)
                    operation = self.client.operations.get(operation=operation)

                if operation.error:
                    raise GeminiError(f"Video operation failed: {operation.error}")
                result = operation.result
            else:
                result = operation

            # Bypass Pydantic dump crash
            outputs = []
            for video in getattr(result, "videos", []):
                v_bytes = getattr(video, "video_bytes", None) or getattr(
                    video, "video", None
                )
                v_uri = getattr(video, "uri", None)
                if v_bytes:
                    outputs.append({"video_bytes": v_bytes})
                elif v_uri:
                    import urllib.request

                    try:
                        req = urllib.request.urlopen(v_uri)
                        outputs.append({"video_bytes": req.read()})
                    except Exception as e:
                        logger.warning("Failed to download video URI %s: %s", v_uri, e)
                        outputs.append({"uri": v_uri})

            return outputs
        except Exception as e:
            logger.error("Failed to generate videos: %s", e)
            raise GeminiError(f"Failed to generate videos: {e}") from e

    def upload_file(
        self, file_path: str, mime_type: str | None = None
    ) -> dict[str, Any]:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            config = types.UploadFileConfig(mime_type=mime_type) if mime_type else None
            file_ref = self.client.files.upload(file=file_path, config=config)
            return file_ref.model_dump()
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to upload file: %s", e)
            raise GeminiError(f"Failed to upload file: {e}") from e

    def list_files(self) -> list[dict[str, Any]]:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return [f.model_dump() for f in self.client.files.list()]
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to list files: %s", e)
            raise GeminiError(f"Failed to list files: {e}") from e

    def get_file(self, file_name: str) -> dict[str, Any]:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return self.client.files.get(name=file_name).model_dump()
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to get file %s: %s", file_name, e)
            raise GeminiError(f"Failed to get file {file_name}: {e}") from e

    def delete_file(self, file_name: str) -> bool:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            self.client.files.delete(name=file_name)
            return True
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to delete file %s: %s", file_name, e)
            raise GeminiError(f"Failed to delete file {file_name}: {e}") from e

    def create_cached_content(
        self,
        model: str,
        contents: Any,
        ttl: str | None = None,
        display_name: str | None = None,
    ) -> dict[str, Any]:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            config = types.CreateCachedContentConfig(
                contents=contents, ttl=ttl, display_name=display_name
            )
            return self.client.caches.create(
                model=model, config=config
            ).model_dump()
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to create cached content: %s", e)
            raise GeminiError(f"Failed to create cached content: {e}") from e

    def list_cached_contents(self) -> list[dict[str, Any]]:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return [c.model_dump() for c in self.client.caches.list()]
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to list cached contents: %s", e)
            raise GeminiError(f"Failed to list cached contents: {e}") from e

    def get_cached_content(self, name: str) -> dict[str, Any]:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return self.client.caches.get(name=name).model_dump()
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to get cached content %s: %s", name, e)
            raise GeminiError(f"Failed to get cached content {name}: {e}") from e

    def delete_cached_content(self, name: str) -> bool:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            self.client.caches.delete(name=name)
            return True
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to delete cached content %s: %s", name, e)
            raise GeminiError(f"Failed to delete cached content {name}: {e}") from e

    def update_cached_content(
        self, name: str, ttl: str | None = None
    ) -> dict[str, Any]:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return self.client.caches.update(
                name=name, config=types.UpdateCachedContentConfig(ttl=ttl)
            ).model_dump()
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to update cached content %s: %s", name, e)
            raise GeminiError(f"Failed to update cached content {name}: {e}") from e

    def create_tuned_model(
        self,
        source_model: str,
        training_data: Any,
        display_name: str | None = None,
        epochs: int | None = None,
    ) -> dict[str, Any]:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            job = self.client.tunings.tune(
                base_model=source_model,
                training_data=training_data,
                config=types.CreateTunedModelConfig(
                    display_name=display_name, epoch_count=epochs
                ),
            )
            return job.model_dump()
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to create tuned model: %s", e)
            raise GeminiError(f"Failed to create tuned model: {e}") from e

    def list_tuned_models(self) -> list[dict[str, Any]]:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return [m.model_dump() for m in self.client.tunings.list()]
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to list tuned models: %s", e)
            raise GeminiError(f"Failed to list tuned models: {e}") from e

    def get_tuned_model(self, name: str) -> dict[str, Any]:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return self.client.tunings.get(name=name).model_dump()
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to get tuned model %s: %s", name, e)
            raise GeminiError(f"Failed to get tuned model {name}: {e}") from e

    def delete_tuned_model(self, name: str) -> bool:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            self.client.tunings.delete(name=name)
            return True
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to delete tuned model %s: %s", name, e)
            raise GeminiError(f"Failed to delete tuned model {name}: {e}") from e

    def create_batch(
        self, requests: list[Any], model: str | None = None
    ) -> dict[str, Any]:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return self.client.batches.create(
                model=model or self.default_model,
                src=requests,
            ).model_dump()
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to create batch: %s", e)
            raise GeminiError(f"Failed to create batch: {e}") from e

    def get_batch(self, name: str) -> dict[str, Any]:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return self.client.batches.get(name=name).model_dump()
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to get batch %s: %s", name, e)
            raise GeminiError(f"Failed to get batch {name}: {e}") from e

    def list_batches(self) -> list[dict[str, Any]]:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return [b.model_dump() for b in self.client.batches.list()]
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to list batches: %s", e)
            raise GeminiError(f"Failed to list batches: {e}") from e

    def delete_batch(self, name: str) -> bool:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            self.client.batches.delete(name=name)
            return True
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to delete batch %s: %s", name, e)
            raise GeminiError(f"Failed to delete batch {name}: {e}") from e
