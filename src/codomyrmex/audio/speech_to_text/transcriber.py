"""High-level transcriber interface for speech-to-text.

This module provides a user-friendly interface for transcribing audio files
using various STT providers.
"""

import asyncio
from collections.abc import AsyncIterator
from pathlib import Path

from .models import (
    TranscriptionConfig,
    TranscriptionResult,
    WhisperModelSize,
)
from .providers import STTProvider, get_provider


class Transcriber:
    """High-level interface for speech-to-text transcription.

    The Transcriber provides a simple, consistent API for transcribing audio
    files using different STT providers.

    Example:
        ```python
        # Basic usage
        transcriber = Transcriber()
        result = transcriber.transcribe("interview.mp3")
        print(result.text)

        # With larger model for better accuracy
        transcriber = Transcriber(model_size=WhisperModelSize.LARGE_V3)
        result = transcriber.transcribe("spanish.wav", language="es")

        # Export to subtitles
        with open("subs.srt", "w") as f:
            f.write(result.to_srt())
        ```

    Attributes:
        provider: The underlying STT provider
        model_size: Current model size (if applicable)
    """

    def __init__(
        self,
        provider: str = "whisper",
        model_size: WhisperModelSize = WhisperModelSize.BASE,
        device: str = "auto",
        compute_type: str = "auto",
        **kwargs: object,
    ) -> None:
        """Initialize the transcriber.

        Args:
            provider: STT provider to use ("whisper")
            model_size: Model size for Whisper provider
            device: Device to run on ("auto", "cpu", "cuda")
            compute_type: Computation type ("auto", "float16", "int8")
            **kwargs: Additional provider-specific arguments

        Raises:
            ProviderNotAvailableError: If provider dependencies are missing
        """
        self._provider_name = provider
        self.model_size = model_size

        self._provider: STTProvider = get_provider(
            provider,
            model_size=model_size,
            device=device,
            compute_type=compute_type,
            **kwargs,
        )

    @property
    def provider(self) -> STTProvider:
        """Get the underlying STT provider."""
        return self._provider

    def transcribe(
        self,
        audio_path: str | Path,
        language: str | None = None,
        task: str = "transcribe",
        word_timestamps: bool = True,
        vad_filter: bool = True,
        **kwargs: object,
    ) -> TranscriptionResult:
        """Transcribe an audio file.

        Args:
            audio_path: Path to the audio file
            language: Language code (None for auto-detection)
            task: "transcribe" or "translate" (translate to English)
            word_timestamps: Include word-level timing
            vad_filter: Filter non-speech segments
            **kwargs: Additional transcription options

        Returns:
            TranscriptionResult with text, segments, and metadata

        Raises:
            TranscriptionError: If transcription fails
            AudioFormatError: If audio format is not supported
        """
        config = TranscriptionConfig(
            language=language,
            task=task,
            word_timestamps=word_timestamps,
            vad_filter=vad_filter,
            **kwargs,  # type: ignore
        )

        return self._provider.transcribe(audio_path, config)

    async def transcribe_async(
        self,
        audio_path: str | Path,
        language: str | None = None,
        task: str = "transcribe",
        word_timestamps: bool = True,
        vad_filter: bool = True,
        **kwargs: object,
    ) -> TranscriptionResult:
        """Transcribe an audio file asynchronously.

        Args:
            audio_path: Path to the audio file
            language: Language code (None for auto-detection)
            task: "transcribe" or "translate"
            word_timestamps: Include word-level timing
            vad_filter: Filter non-speech segments
            **kwargs: Additional transcription options

        Returns:
            TranscriptionResult with text and segments
        """
        config = TranscriptionConfig(
            language=language,
            task=task,
            word_timestamps=word_timestamps,
            vad_filter=vad_filter,
            **kwargs,  # type: ignore
        )

        return await self._provider.transcribe_async(audio_path, config)

    async def transcribe_stream(
        self,
        audio_path: str | Path,
        language: str | None = None,
        **kwargs: object,
    ) -> AsyncIterator[TranscriptionResult]:
        """Stream transcription results as they become available.

        Args:
            audio_path: Path to the audio file
            language: Language code (None for auto-detection)
            **kwargs: Additional transcription options

        Yields:
            Partial TranscriptionResult as segments complete
        """
        config = TranscriptionConfig(
            language=language,
            **kwargs,  # type: ignore
        )

        async for result in self._provider.transcribe_stream(audio_path, config):
            yield result

    def detect_language(
        self,
        audio_path: str | Path,
    ) -> tuple[str, float]:
        """Detect the language of an audio file.

        Args:
            audio_path: Path to the audio file

        Returns:
            Tuple of (language_code, confidence)
        """
        return self._provider.detect_language(audio_path)

    def transcribe_batch(
        self,
        audio_paths: list[str | Path],
        language: str | None = None,
        **kwargs: object,
    ) -> list[TranscriptionResult]:
        """Transcribe multiple audio files.

        Args:
            audio_paths: List of paths to audio files
            language: Language code (None for auto-detection)
            **kwargs: Additional transcription options

        Returns:
            List of TranscriptionResult objects
        """
        results = []
        for path in audio_paths:
            result = self.transcribe(path, language=language, **kwargs)
            results.append(result)
        return results

    async def transcribe_batch_async(
        self,
        audio_paths: list[str | Path],
        language: str | None = None,
        max_concurrent: int = 3,
        **kwargs: object,
    ) -> list[TranscriptionResult]:
        """Transcribe multiple audio files concurrently.

        Args:
            audio_paths: List of paths to audio files
            language: Language code (None for auto-detection)
            max_concurrent: Maximum concurrent transcriptions
            **kwargs: Additional transcription options

        Returns:
            List of TranscriptionResult objects (in same order as input)
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def transcribe_with_semaphore(path: str | Path) -> TranscriptionResult:
            async with semaphore:
                return await self.transcribe_async(path, language=language, **kwargs)

        tasks = [transcribe_with_semaphore(path) for path in audio_paths]
        return await asyncio.gather(*tasks)

    def get_supported_languages(self) -> list[str]:
        """Get list of supported language codes.

        Returns:
            List of ISO 639-1 language codes
        """
        return self._provider.get_supported_languages()

    @property
    def is_loaded(self) -> bool:
        """Check if the model is loaded and ready."""
        return self._provider.is_loaded

    def unload(self) -> None:
        """Unload the model to free memory."""
        self._provider.unload()

    def __enter__(self) -> "Transcriber":
        """Context manager entry."""
        return self

    def __exit__(self, *args: object) -> None:
        """Context manager exit - unload model."""
        self.unload()


__all__ = ["Transcriber"]
