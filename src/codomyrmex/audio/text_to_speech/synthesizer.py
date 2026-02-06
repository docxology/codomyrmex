"""High-level synthesizer interface for text-to-speech.

This module provides a user-friendly interface for synthesizing speech
using various TTS providers.
"""

import asyncio
from pathlib import Path


from .models import SynthesisResult, TTSConfig, VoiceInfo
from .providers import TTSProvider, get_provider


class Synthesizer:
    """High-level interface for text-to-speech synthesis.

    The Synthesizer provides a simple, consistent API for converting text
    to speech using different TTS providers.

    Example:
        ```python
        # Offline synthesis (fast, uses system voices)
        synth = Synthesizer(provider="pyttsx3")
        result = synth.synthesize("Hello world!")
        result.save("hello.wav")

        # Neural TTS (high quality, requires internet)
        synth = Synthesizer(provider="edge-tts")
        result = synth.synthesize("Hello!", voice="en-US-AriaNeural")
        result.save("hello.mp3")

        # Async usage
        result = await synth.synthesize_async("Hello!")
        ```

    Attributes:
        provider: The underlying TTS provider
    """

    def __init__(
        self,
        provider: str = "pyttsx3",
        config: TTSConfig | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize the synthesizer.

        Args:
            provider: TTS provider to use ("pyttsx3", "edge-tts")
            config: Default configuration for synthesis
            **kwargs: Additional provider-specific arguments

        Raises:
            ProviderNotAvailableError: If provider dependencies are missing
        """
        self._provider_name = provider
        self._default_config = config or TTSConfig()

        self._provider: TTSProvider = get_provider(provider, **kwargs)

    @property
    def provider(self) -> TTSProvider:
        """Get the underlying TTS provider."""
        return self._provider

    def synthesize(
        self,
        text: str,
        voice: str | None = None,
        rate: float = 1.0,
        pitch: float = 1.0,
        volume: float = 1.0,
        **kwargs: object,
    ) -> SynthesisResult:
        """Synthesize speech from text.

        Args:
            text: Text to synthesize
            voice: Voice ID to use (None for default)
            rate: Speaking rate (0.5 = half speed, 2.0 = double)
            pitch: Voice pitch adjustment
            volume: Output volume (0.0 - 1.0)
            **kwargs: Additional synthesis options

        Returns:
            SynthesisResult with audio data

        Raises:
            SynthesisError: If synthesis fails
            VoiceNotFoundError: If requested voice is not available
        """
        config = TTSConfig(
            voice=voice or self._default_config.voice,
            language=self._default_config.language,
            rate=rate,
            pitch=pitch,
            volume=volume,
            format=self._default_config.format,
            sample_rate=self._default_config.sample_rate,
        )

        return self._provider.synthesize(text, config)

    async def synthesize_async(
        self,
        text: str,
        voice: str | None = None,
        rate: float = 1.0,
        pitch: float = 1.0,
        volume: float = 1.0,
        **kwargs: object,
    ) -> SynthesisResult:
        """Synthesize speech from text asynchronously.

        Args:
            text: Text to synthesize
            voice: Voice ID to use (None for default)
            rate: Speaking rate
            pitch: Voice pitch adjustment
            volume: Output volume
            **kwargs: Additional synthesis options

        Returns:
            SynthesisResult with audio data
        """
        config = TTSConfig(
            voice=voice or self._default_config.voice,
            language=self._default_config.language,
            rate=rate,
            pitch=pitch,
            volume=volume,
        )

        return await self._provider.synthesize_async(text, config)

    def synthesize_to_file(
        self,
        text: str,
        output_path: str | Path,
        voice: str | None = None,
        rate: float = 1.0,
        **kwargs: object,
    ) -> Path:
        """Synthesize speech and save directly to a file.

        Args:
            text: Text to synthesize
            output_path: Output file path
            voice: Voice ID to use
            rate: Speaking rate
            **kwargs: Additional synthesis options

        Returns:
            Path to the saved file
        """
        result = self.synthesize(text, voice=voice, rate=rate, **kwargs)
        return result.save(output_path)

    async def synthesize_to_file_async(
        self,
        text: str,
        output_path: str | Path,
        voice: str | None = None,
        rate: float = 1.0,
        **kwargs: object,
    ) -> Path:
        """Synthesize speech and save to file asynchronously.

        Args:
            text: Text to synthesize
            output_path: Output file path
            voice: Voice ID to use
            rate: Speaking rate
            **kwargs: Additional synthesis options

        Returns:
            Path to the saved file
        """
        result = await self.synthesize_async(text, voice=voice, rate=rate, **kwargs)
        return result.save(output_path)

    def synthesize_batch(
        self,
        texts: list[str],
        voice: str | None = None,
        **kwargs: object,
    ) -> list[SynthesisResult]:
        """Synthesize multiple texts.

        Args:
            texts: List of texts to synthesize
            voice: Voice ID to use for all
            **kwargs: Additional synthesis options

        Returns:
            List of SynthesisResult objects
        """
        results = []
        for text in texts:
            result = self.synthesize(text, voice=voice, **kwargs)
            results.append(result)
        return results

    async def synthesize_batch_async(
        self,
        texts: list[str],
        voice: str | None = None,
        max_concurrent: int = 5,
        **kwargs: object,
    ) -> list[SynthesisResult]:
        """Synthesize multiple texts concurrently.

        Args:
            texts: List of texts to synthesize
            voice: Voice ID to use for all
            max_concurrent: Maximum concurrent synthesis operations
            **kwargs: Additional synthesis options

        Returns:
            List of SynthesisResult objects (in same order as input)
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def synthesize_with_semaphore(text: str) -> SynthesisResult:
            async with semaphore:
                return await self.synthesize_async(text, voice=voice, **kwargs)

        tasks = [synthesize_with_semaphore(text) for text in texts]
        return await asyncio.gather(*tasks)

    def list_voices(
        self,
        language: str | None = None,
    ) -> list[VoiceInfo]:
        """List available voices.

        Args:
            language: Filter by language code (e.g., "en-US", "es")

        Returns:
            List of VoiceInfo objects
        """
        return self._provider.list_voices(language)

    def get_voice(self, voice_id: str) -> VoiceInfo | None:
        """Get information about a specific voice.

        Args:
            voice_id: Voice identifier

        Returns:
            VoiceInfo if found, None otherwise
        """
        return self._provider.get_voice(voice_id)

    def get_supported_languages(self) -> list[str]:
        """Get list of supported language codes.

        Returns:
            List of language codes (e.g., ["en-US", "es-ES"])
        """
        return self._provider.get_supported_languages()

    @property
    def default_voice(self) -> str:
        """Get the default voice ID for the current provider."""
        return self._provider.default_voice

    def set_default_voice(self, voice_id: str) -> None:
        """Set the default voice for all synthesis operations.

        Args:
            voice_id: Voice identifier to use as default
        """
        self._default_config.voice = voice_id

    def set_default_language(self, language: str) -> None:
        """Set the default language.

        Args:
            language: Language code (e.g., "en-US")
        """
        self._default_config.language = language


__all__ = ["Synthesizer"]
