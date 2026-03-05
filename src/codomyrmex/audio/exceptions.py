"""Audio module exception classes.

This module defines all exception classes for audio processing operations
including speech-to-text transcription and text-to-speech synthesis.

Exception Hierarchy:
    AudioError (base)
    ├── TranscriptionError - Speech-to-text errors
    ├── SynthesisError - Text-to-speech errors
    ├── AudioFormatError - Unsupported or invalid audio format
    ├── ModelNotLoadedError - Model not loaded or unavailable
    ├── ProviderNotAvailableError - Provider dependencies missing
    └── VoiceNotFoundError - Requested voice not available
"""

from pathlib import Path
from typing import Any

from codomyrmex.exceptions import CodomyrmexError


class AudioError(CodomyrmexError):
    """Base exception for all audio-related errors.

    Attributes:
        message: The error message
        audio_path: Path to the audio file involved, if any
        context: Additional context information

    """

    def __init__(
        self,
        message: str,
        audio_path: str | Path | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize AudioError.

        Args:
            message: The error message
            audio_path: Path to the audio file involved, if any
            **kwargs: Additional context

        """
        super().__init__(message, **kwargs)
        if audio_path:
            self.context["audio_path"] = str(audio_path)


class TranscriptionError(AudioError):
    """Raised when speech-to-text transcription fails.

    This can occur due to:
    - Invalid or corrupted audio file
    - Unsupported audio format
    - Model inference failure
    - Language detection failure
    """

    def __init__(
        self,
        message: str,
        audio_path: str | Path | None = None,
        language: str | None = None,
        model_size: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize TranscriptionError.

        Args:
            message: The error message
            audio_path: Path to the audio file involved
            language: Language code involved
            model_size: Model size involved
            **kwargs: Additional context

        """
        super().__init__(message, audio_path=audio_path, **kwargs)
        if language:
            self.context["language"] = language
        if model_size:
            self.context["model_size"] = model_size


class SynthesisError(AudioError):
    """Raised when text-to-speech synthesis fails.

    This can occur due to:
    - Empty or invalid text input
    - Voice synthesis failure
    - Output file writing failure
    - Provider API errors
    """

    def __init__(
        self,
        message: str,
        text: str | None = None,
        voice_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize SynthesisError.

        Args:
            message: The error message
            text: Text that failed to synthesize
            voice_id: Voice ID involved
            **kwargs: Additional context

        """
        super().__init__(message, **kwargs)
        if text:
            # Truncate long text for context
            self.context["text"] = text[:100] + "..." if len(text) > 100 else text
        if voice_id:
            self.context["voice_id"] = voice_id


class AudioFormatError(AudioError):
    """Raised when the audio format is unsupported or invalid.

    Supported formats typically include:
    - WAV, MP3, FLAC, OGG, M4A, WEBM for input
    - WAV, MP3 for output
    """

    def __init__(
        self,
        message: str,
        format_type: str | None = None,
        supported_formats: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize AudioFormatError.

        Args:
            message: The error message
            format_type: The invalid format
            supported_formats: List of supported formats
            **kwargs: Additional context

        """
        super().__init__(message, **kwargs)
        if format_type:
            self.context["format_type"] = format_type
        if supported_formats:
            self.context["supported_formats"] = supported_formats


class ModelNotLoadedError(AudioError):
    """Raised when the required model is not loaded or unavailable.

    This can occur when:
    - Model has not been initialized
    - Model download failed
    - Model file is corrupted
    - Insufficient memory to load model
    """

    def __init__(
        self,
        message: str,
        model_name: str | None = None,
        model_size: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize ModelNotLoadedError.

        Args:
            message: The error message
            model_name: Name of the model
            model_size: Size of the model
            **kwargs: Additional context

        """
        super().__init__(message, **kwargs)
        if model_name:
            self.context["model_name"] = model_name
        if model_size:
            self.context["model_size"] = model_size


class ProviderNotAvailableError(AudioError):
    """Raised when a provider's dependencies are not installed.

    Install the required dependencies with:
        uv sync --extra audio
    """

    def __init__(
        self,
        message: str,
        provider_name: str | None = None,
        missing_packages: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize ProviderNotAvailableError.

        Args:
            message: The error message
            provider_name: Name of the provider
            missing_packages: List of missing packages
            **kwargs: Additional context

        """
        super().__init__(message, **kwargs)
        if provider_name:
            self.context["provider_name"] = provider_name
        if missing_packages:
            self.context["missing_packages"] = missing_packages


class VoiceNotFoundError(AudioError):
    """Raised when the requested voice is not available.

    This can occur when:
    - Voice ID does not exist for the provider
    - Voice is not available for the specified language
    - Voice requires additional installation
    """

    def __init__(
        self,
        message: str,
        voice_id: str | None = None,
        available_voices: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize VoiceNotFoundError.

        Args:
            message: The error message
            voice_id: The missing voice ID
            available_voices: List of available voices
            **kwargs: Additional context

        """
        super().__init__(message, **kwargs)
        if voice_id:
            self.context["voice_id"] = voice_id
        if available_voices:
            self.context["available_voices"] = available_voices[
                :10
            ]  # Limit for display


__all__ = [
    "AudioError",
    "AudioFormatError",
    "ModelNotLoadedError",
    "ProviderNotAvailableError",
    "SynthesisError",
    "TranscriptionError",
    "VoiceNotFoundError",
]
