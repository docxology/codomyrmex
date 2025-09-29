"""High-level integration utilities for Ollama language models."""

import asyncio
import logging
from typing import AsyncGenerator, Dict, List, Optional, Union

from .config import get_config
from .ollama_client import OllamaClient, OllamaError, OllamaConnectionError, OllamaModelError

logger = logging.getLogger(__name__)

# Get global configuration
_config = get_config()


class OllamaManager:
    """
    High-level manager for Ollama operations with connection pooling and error handling.
    """

    def __init__(self, **client_kwargs):
        """
        Initialize Ollama manager.

        Args:
            **client_kwargs: Arguments to pass to OllamaClient
        """
        self.client = OllamaClient(**client_kwargs)
        self._default_options = {}

    def set_default_options(self, **options):
        """
        Set default generation options.

        Args:
            **options: Options like temperature, top_p, etc.
        """
        self._default_options.update(options)

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        options: Optional[Dict] = None,
        stream: bool = False,
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Generate text with automatic error handling and retries.

        Args:
            prompt: Input prompt
            model: Model to use
            options: Generation options
            stream: Whether to stream

        Returns:
            Generated text or async generator
        """
        # Merge options with defaults
        merged_options = {**self._default_options}
        if options:
            merged_options.update(options)

        try:
            return self.client.generate(
                prompt=prompt,
                model=model,
                options=merged_options or None,
                stream=stream
            )
        except OllamaError as e:
            logger.error(f"Generation failed: {e}")
            raise

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        options: Optional[Dict] = None,
        stream: bool = False,
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Chat completion with automatic error handling.

        Args:
            messages: Message history
            model: Model to use
            options: Generation options
            stream: Whether to stream

        Returns:
            Generated response or async generator
        """
        # Merge options with defaults
        merged_options = {**self._default_options}
        if options:
            merged_options.update(options)

        try:
            return self.client.chat(
                messages=messages,
                model=model,
                options=merged_options or None,
                stream=stream
            )
        except OllamaError as e:
            logger.error(f"Chat completion failed: {e}")
            raise

    def list_models(self) -> List[Dict]:
        """List available models."""
        try:
            return self.client.list_models()
        except OllamaError as e:
            logger.error(f"Failed to list models: {e}")
            raise

    def check_health(self) -> bool:
        """
        Check if Ollama server is healthy.

        Returns:
            True if server is accessible
        """
        try:
            models = self.client.list_models()
            return len(models) > 0
        except OllamaError:
            return False

    def close(self):
        """Close the underlying client."""
        self.client.close()


# Global instances for convenience
_default_manager: Optional[OllamaManager] = None


def get_default_manager(**client_kwargs) -> OllamaManager:
    """
    Get or create default Ollama manager instance.

    Args:
        **client_kwargs: Arguments for OllamaClient if creating new instance

    Returns:
        Default OllamaManager instance
    """
    global _default_manager
    if _default_manager is None:
        _default_manager = OllamaManager(**client_kwargs)
    return _default_manager


def generate_with_ollama(
    prompt: str,
    model: Optional[str] = None,
    options: Optional[Dict] = None,
    base_url: Optional[str] = None,
    timeout: Optional[int] = None,
) -> str:
    """
    Convenience function for simple text generation.

    Args:
        prompt: Input prompt
        model: Model to use (defaults to config)
        options: Generation options
        base_url: Ollama server URL (defaults to config)
        timeout: Request timeout (defaults to config)

    Returns:
        Generated text
    """
    manager = get_default_manager(
        model=model or _config.model,
        base_url=base_url or _config.base_url,
        timeout=timeout or _config.timeout
    )
    return manager.generate(prompt, options=options)


async def stream_with_ollama(
    prompt: str,
    model: Optional[str] = None,
    options: Optional[Dict] = None,
    base_url: Optional[str] = None,
    timeout: Optional[int] = None,
) -> AsyncGenerator[str, None]:
    """
    Convenience function for streaming text generation.

    Args:
        prompt: Input prompt
        model: Model to use (defaults to config)
        options: Generation options
        base_url: Ollama server URL (defaults to config)
        timeout: Request timeout (defaults to config)

    Yields:
        Generated text chunks
    """
    manager = get_default_manager(
        model=model or _config.model,
        base_url=base_url or _config.base_url,
        timeout=timeout or _config.timeout
    )
    async for chunk in manager.generate(prompt, stream=True, options=options):
        yield chunk


def chat_with_ollama(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    options: Optional[Dict] = None,
    base_url: Optional[str] = None,
    timeout: Optional[int] = None,
) -> str:
    """
    Convenience function for chat completion.

    Args:
        messages: Message history
        model: Model to use (defaults to config)
        options: Generation options
        base_url: Ollama server URL (defaults to config)
        timeout: Request timeout (defaults to config)

    Returns:
        Generated response
    """
    manager = get_default_manager(
        model=model or _config.model,
        base_url=base_url or _config.base_url,
        timeout=timeout or _config.timeout
    )
    return manager.chat(messages, options=options)


async def stream_chat_with_ollama(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    options: Optional[Dict] = None,
    base_url: Optional[str] = None,
    timeout: Optional[int] = None,
) -> AsyncGenerator[str, None]:
    """
    Convenience function for streaming chat completion.

    Args:
        messages: Message history
        model: Model to use (defaults to config)
        options: Generation options
        base_url: Ollama server URL (defaults to config)
        timeout: Request timeout (defaults to config)

    Yields:
        Generated response chunks
    """
    manager = get_default_manager(
        model=model or _config.model,
        base_url=base_url or _config.base_url,
        timeout=timeout or _config.timeout
    )
    async for chunk in manager.chat(messages, stream=True, options=options):
        yield chunk


def check_ollama_availability(
    base_url: Optional[str] = None,
    timeout: Optional[int] = None,
) -> bool:
    """
    Check if Ollama server is available.

    Args:
        base_url: Ollama server URL (defaults to config)
        timeout: Connection timeout (defaults to config)

    Returns:
        True if server is available
    """
    try:
        client = OllamaClient(
            base_url=base_url or _config.base_url,
            timeout=timeout or _config.timeout
        )
        return client._check_connection()
    except Exception:
        return False
    finally:
        try:
            client.close()
        except:
            pass


def get_available_models(
    base_url: Optional[str] = None,
    timeout: Optional[int] = None,
) -> List[str]:
    """
    Get list of available model names.

    Args:
        base_url: Ollama server URL (defaults to config)
        timeout: Request timeout (defaults to config)

    Returns:
        List of model names
    """
    try:
        client = OllamaClient(
            base_url=base_url or _config.base_url,
            timeout=timeout or _config.timeout
        )
        models = client.list_models()
        return [model.get("name", "") for model in models]
    except OllamaError:
        return []
    finally:
        try:
            client.close()
        except:
            pass


def create_chat_messages(
    system_prompt: Optional[str] = None,
    user_message: str = "",
    conversation_history: Optional[List[Dict[str, str]]] = None,
) -> List[Dict[str, str]]:
    """
    Create chat message format for Ollama.

    Args:
        system_prompt: Optional system message
        user_message: User message
        conversation_history: Previous conversation messages

    Returns:
        Formatted message list
    """
    messages = []

    if conversation_history:
        messages.extend(conversation_history)

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    if user_message:
        messages.append({"role": "user", "content": user_message})

    return messages
