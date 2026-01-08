from pathlib import Path
from typing import Any, Iterator, Optional, List, Dict, Union
import os

from PIL import Image
from google import genai
from google.genai import types

from codomyrmex.agents.config import get_config
from codomyrmex.agents.core import (
from codomyrmex.agents.exceptions import AgentError, GeminiError
from codomyrmex.logging_monitoring import get_logger




"""Gemini API client wrapper using google-genai SDK."""


# Try to import google-genai, handle if not installed yet
try:
except ImportError:
    genai = None

    AgentCapabilities,
    AgentRequest,
    AgentResponse,
    BaseAgent,
)

logger = get_logger(__name__)


class GeminiClient(BaseAgent):
    """Client for interacting with Gemini API via google-genai SDK."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
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

        self.api_key = self.get_config_value("gemini_api_key", config=config) or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("No GEMINI_API_KEY found. Some operations will fail.")

        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Client: {e}")
            self.client = None

        self.default_model = self.get_config_value("gemini_model", default="gemini-2.0-flash", config=config)

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        if not self.client:
            raise GeminiError("Gemini Client not initialized")

        prompt = request.prompt
        context = request.context or {}
        model = context.get("model", self.default_model)
        
        # Build Config
        config_params = {}
        
        # 1. Structured Output / JSON Mode
        if "response_schema" in context:
             config_params["response_mime_type"] = "application/json"
             config_params["response_schema"] = context["response_schema"]
        
        # 2. System Instructions
        if "system_instruction" in context:
             config_params["system_instruction"] = context["system_instruction"]

        # 3. Safety Settings
        if "safety_settings" in context:
             config_params["safety_settings"] = context["safety_settings"]

        # 4. Tools (Function Calling, Code Execution, Google Search)
        # Expecting context['tools'] to be a list of tool definitions or predefined strings
        if "tools" in context:
             tools_config = []
             for tool in context["tools"]:
                 if isinstance(tool, str):
                     if tool == "code_execution":
                         tools_config.append(types.Tool(code_execution=types.CodeExecution()))
                     elif tool == "google_search":
                         # Check SDK specific syntax for Grounding/Search tool
                         tools_config.append(types.Tool(google_search=types.GoogleSearch()))
                 else:
                     # Assume it's a Tool object or dict conformant to SDK
                     tools_config.append(tool)
             config_params["tools"] = tools_config

        # 5. Tool Config (Mode)
        if "tool_config" in context:
             config_params["tool_config"] = context["tool_config"]

        # 6. Cached Content
        if "cached_content" in context:
             config_params["cached_content"] = context["cached_content"]

        contents = self._build_contents(prompt, context)

        try:
            response = self.client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(**config_params) if config_params else None
            )
            return self._build_response_from_api_result(response, request)
        except Exception as e:
            raise GeminiError(f"Gemini API execution failed: {e}") from e

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        if not self.client:
             raise GeminiError("Gemini Client not initialized")

        prompt = request.prompt
        context = request.context or {}
        model = context.get("model", self.default_model)
        contents = self._build_contents(prompt, context)
        
        # Similar config logic for streaming
        config_params = {}
        if "system_instruction" in context: config_params["system_instruction"] = context["system_instruction"]
        # ... (rest of config logic ideally shared)

        try:
            response_stream = self.client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(**config_params) if config_params else None
            )
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Gemini streaming failed: {e}")
            yield f"\n[Error: {e}]"

    def _build_contents(self, prompt: str, context: Dict[str, Any]) -> List[Any]:
        if "contents" in context: return context["contents"]
        
        parts = [prompt]
        if "images" in context:
             for img_path in context["images"]:
                 try:
                     img = Image.open(img_path)
                     parts.append(img)
                 except Exception as e:
                     logger.warning(f"Failed to load image: {e}")
        return [parts]

    def _build_response_from_api_result(self, response: Any, request: AgentRequest) -> AgentResponse:
        if not response.candidates:
             # Check if it was a prompt feedback block
             return AgentResponse(content="", error="No candidates returned", metadata={"raw": str(response)})
        
        cand = response.candidates[0]
        content = ""
        
        # Handle Parts (Text vs Function Call)
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
                "usage": response.usage_metadata.model_dump() if response.usage_metadata else {},
            }
        )

    # --- Core API Methods ---
    def list_models(self) -> List[Dict[str, Any]]:
        if not self.client: return []
        try:
             return [m.model_dump() for m in self.client.models.list()]
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

    def get_model(self, model_name: str) -> Optional[Dict[str, Any]]:
        if not self.client: return None
        try:
             return self.client.models.get(model=model_name).model_dump()
        except Exception as e: return None

    def count_tokens(self, content: Union[str, List[Any]], model: Optional[str] = None) -> int:
        if not self.client: return 0
        try:
            return self.client.models.count_tokens(model=model or self.default_model, contents=content).total_tokens
        except Exception as e: return 0

    def embed_content(self, content: Union[str, List[str]], model: str = "text-embedding-004") -> List[List[float]]:
        if not self.client: return []
        try:
            resp = self.client.models.embed_content(model=model, contents=content)
            if hasattr(resp, 'embedding'): return [resp.embedding.values]
            if hasattr(resp, 'embeddings'): return [e.values for e in resp.embeddings]
            return []
        except Exception as e: return []

    # --- Files API ---
    def upload_file(self, file_path: str, mime_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not self.client: return None
        try:
            # Corrected signature: file=path
            file_ref = self.client.files.upload(file=file_path, config=types.UploadFileConfig(mime_type=mime_type) if mime_type else None)
            return file_ref.model_dump()
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            return None

    def list_files(self) -> List[Dict[str, Any]]:
        if not self.client: return []
        try:
            return [f.model_dump() for f in self.client.files.list()]
        except Exception as e: return []

    def delete_file(self, file_name: str) -> bool:
        if not self.client: return False
        try:
            self.client.files.delete(name=file_name)
            return True
        except Exception: return False

    # --- Caching API ---
    def create_cached_content(self, model: str, contents: Any, ttl: Optional[str] = None, display_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not self.client: return None
        try:
             config = types.CreateCachedContentConfig(model=model, contents=contents, ttl=ttl, display_name=display_name)
             return self.client.caches.create(config=config).model_dump()
        except Exception as e: return None

    def list_cached_contents(self) -> List[Dict[str, Any]]:
        if not self.client: return []
        try:
             return [c.model_dump() for c in self.client.caches.list()]
        except Exception: return []

    def get_cached_content(self, name: str) -> Optional[Dict[str, Any]]:
        if not self.client: return None
        try:
             return self.client.caches.get(name=name).model_dump()
        except Exception: return None

    def delete_cached_content(self, name: str) -> bool:
        if not self.client: return False
        try:
             self.client.caches.delete(name=name)
             return True
        except Exception: return False

    def update_cached_content(self, name: str, ttl: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not self.client: return None
        try:
             return self.client.caches.update(name=name, config=types.UpdateCachedContentConfig(ttl=ttl)).model_dump()
        except Exception: return None

    # --- Tuning API ---
    def create_tuned_model(self, source_model: str, training_data: Any, display_name: Optional[str] = None, epochs: Optional[int] = None) -> Optional[Dict[str, Any]]:
        if not self.client: return None
        try:
             job = self.client.tunings.tune(base_model=source_model, training_data=training_data, config=types.CreateTunedModelConfig(display_name=display_name, epoch_count=epochs))
             return job.model_dump()
        except Exception: return None

    def list_tuned_models(self) -> List[Dict[str, Any]]:
        if not self.client: return []
        try:
             return [m.model_dump() for m in self.client.tunings.list()]
        except Exception: return []

    def get_tuned_model(self, name: str) -> Optional[Dict[str, Any]]:
        if not self.client: return None
        try:
             return self.client.tunings.get(name=name).model_dump()
        except Exception: return None

    def delete_tuned_model(self, name: str) -> bool:
        if not self.client: return False
        try:
             self.client.tunings.delete(name=name)
             return True
        except Exception: return False
