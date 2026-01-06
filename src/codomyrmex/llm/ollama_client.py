"""Comprehensive Ollama client with network I/O, async support, and advanced features."""

import asyncio
import json
import logging
import time
from collections.abc import AsyncGenerator
from typing import Optional, Union

import aiohttp
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class OllamaError(Exception):
    """Base exception for Ollama client errors."""
    pass


class OllamaConnectionError(OllamaError):
    """Raised when unable to connect to Ollama server."""
    pass


class OllamaTimeoutError(OllamaError):
    """Raised when request times out."""
    pass


class OllamaModelError(OllamaError):
    """Raised when model-related errors occur."""
    pass


class OllamaClient:
    """
    Comprehensive Ollama client with sync/async support, streaming, and advanced features.

    Supports both synchronous and asynchronous operations, connection pooling,
    retry logic, and comprehensive error handling.
    """

    DEFAULT_BASE_URL = "http://localhost:11434"
    DEFAULT_TIMEOUT = 30
    DEFAULT_MODEL = "llama3.1"

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
        session: Optional[requests.Session] = None,
        verify_ssl: bool = True,
    ):
        """
        Initialize Ollama client.

        Args:
            base_url: Base URL for Ollama server
            model: Default model to use
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            backoff_factor: Backoff factor for retry delays
            session: Optional requests session to use
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.verify_ssl = verify_ssl

        # Setup requests session with retry logic
        self.session = session or self._create_session()
        self._models_cache: Optional[list[dict]] = None
        self._models_cache_time: Optional[float] = None
        self._cache_ttl = 300  # 5 minutes

        logger.info(f"Initialized OllamaClient for {self.base_url} with model {self.model}")

    def _create_session(self) -> requests.Session:
        """Create requests session with retry configuration."""
        session = requests.Session()
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _check_connection(self) -> bool:
        """Check if Ollama server is accessible."""
        try:
            response = self.session.get(
                f"{self.base_url}/api/version",
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            return False

    def list_models(self, use_cache: bool = True) -> list[dict]:
        """
        List available models.

        Args:
            use_cache: Whether to use cached results if available

        Returns:
            List of model information dictionaries
        """
        # Check cache
        if use_cache and self._models_cache and self._models_cache_time:
            if time.time() - self._models_cache_time < self._cache_ttl:
                return self._models_cache

        try:
            response = self.session.get(
                f"{self.base_url}/api/tags",
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()

            data = response.json()
            models = data.get("models", [])

            # Update cache
            self._models_cache = models
            self._models_cache_time = time.time()

            logger.info(f"Found {len(models)} models")
            return models

        except requests.exceptions.RequestException as e:
            raise OllamaConnectionError(f"Failed to list models: {e}")
        except Exception as e:
            raise OllamaError(f"Unexpected error listing models: {e}")

    def check_model_exists(self, model: str) -> bool:
        """
        Check if a specific model exists.

        Args:
            model: Model name to check

        Returns:
            True if model exists, False otherwise
        """
        try:
            models = self.list_models()
            return any(m.get("name") == model for m in models)
        except OllamaError:
            return False

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        options: Optional[dict] = None,
        stream: bool = False,
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Generate text completion.

        Args:
            prompt: Input prompt
            model: Model to use (defaults to instance model)
            options: Generation options (temperature, top_p, etc.)
            stream: Whether to stream the response

        Returns:
            Generated text or async generator for streaming
        """
        model = model or self.model

        if not self.check_model_exists(model):
            raise OllamaModelError(f"Model '{model}' not found")

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
        }

        if options:
            payload["options"] = options

        if stream:
            return self._generate_stream(payload)
        else:
            return self._generate_sync(payload)

    def _generate_sync(self, payload: dict) -> str:
        """Synchronous text generation."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()

            data = response.json()
            return data.get("response", "")

        except requests.exceptions.Timeout:
            raise OllamaTimeoutError("Generation request timed out")
        except requests.exceptions.RequestException as e:
            raise OllamaConnectionError(f"Generation request failed: {e}")
        except Exception as e:
            raise OllamaError(f"Unexpected error during generation: {e}")

    async def _generate_stream(self, payload: dict) -> AsyncGenerator[str, None]:
        """Asynchronous streaming text generation."""
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    verify_ssl=self.verify_ssl
                ) as response:
                    response.raise_for_status()

                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line.decode('utf-8').strip())
                                if "response" in data:
                                    yield data["response"]
                                if data.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue

        except asyncio.TimeoutError:
            raise OllamaTimeoutError("Generation request timed out")
        except aiohttp.ClientError as e:
            raise OllamaConnectionError(f"Generation request failed: {e}")
        except Exception as e:
            raise OllamaError(f"Unexpected error during streaming generation: {e}")

    def chat(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        options: Optional[dict] = None,
        stream: bool = False,
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Chat completion with message history.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (defaults to instance model)
            options: Generation options
            stream: Whether to stream the response

        Returns:
            Generated response or async generator for streaming
        """
        model = model or self.model

        if not self.check_model_exists(model):
            raise OllamaModelError(f"Model '{model}' not found")

        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }

        if options:
            payload["options"] = options

        if stream:
            return self._chat_stream(payload)
        else:
            return self._chat_sync(payload)

    def _chat_sync(self, payload: dict) -> str:
        """Synchronous chat completion."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()

            data = response.json()
            return data.get("message", {}).get("content", "")

        except requests.exceptions.Timeout:
            raise OllamaTimeoutError("Chat request timed out")
        except requests.exceptions.RequestException as e:
            raise OllamaConnectionError(f"Chat request failed: {e}")
        except Exception as e:
            raise OllamaError(f"Unexpected error during chat: {e}")

    async def _chat_stream(self, payload: dict) -> AsyncGenerator[str, None]:
        """Asynchronous streaming chat completion."""
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    verify_ssl=self.verify_ssl
                ) as response:
                    response.raise_for_status()

                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line.decode('utf-8').strip())
                                if "message" in data and "content" in data["message"]:
                                    yield data["message"]["content"]
                                if data.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue

        except asyncio.TimeoutError:
            raise OllamaTimeoutError("Chat request timed out")
        except aiohttp.ClientError as e:
            raise OllamaConnectionError(f"Chat request failed: {e}")
        except Exception as e:
            raise OllamaError(f"Unexpected error during streaming chat: {e}")

    def get_model_info(self, model: Optional[str] = None) -> dict:
        """
        Get detailed information about a model.

        Args:
            model: Model name (defaults to instance model)

        Returns:
            Model information dictionary
        """
        model = model or self.model

        try:
            models = self.list_models()
            for m in models:
                if m.get("name") == model:
                    return m
            raise OllamaModelError(f"Model '{model}' not found")
        except OllamaError:
            raise

    def close(self):
        """Close the client session."""
        if self.session:
            self.session.close()
            logger.info("OllamaClient session closed")
