"""Data models for text-to-speech synthesis.

This module defines the core data structures for TTS results,
voice information, and configuration.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class AudioFormat(Enum):
    """Supported audio output formats."""

    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    FLAC = "flac"


class VoiceGender(Enum):
    """Voice gender classification."""

    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"


@dataclass
class VoiceInfo:
    """Information about an available voice.

    Attributes:
        id: Unique voice identifier
        name: Human-readable voice name
        language: Language code (e.g., "en-US")
        gender: Voice gender
        is_neural: Whether this is a neural/AI voice
        provider: Provider that offers this voice
        description: Optional description of the voice
        sample_rate: Native sample rate in Hz
        styles: Available speaking styles (if supported)
    """

    id: str
    name: str
    language: str
    gender: VoiceGender = VoiceGender.UNKNOWN
    is_neural: bool = False
    provider: str = ""
    description: str = ""
    sample_rate: int = 22050
    styles: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "language": self.language,
            "gender": self.gender.value,
            "is_neural": self.is_neural,
            "provider": self.provider,
            "description": self.description,
            "sample_rate": self.sample_rate,
            "styles": self.styles,
        }


@dataclass
class SynthesisResult:
    """Result of text-to-speech synthesis.

    Attributes:
        audio_data: Raw audio bytes
        format: Audio format
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        voice_id: Voice used for synthesis
        text: Original input text
        provider: Provider that generated the audio
        processing_time: Time taken to synthesize
    """

    audio_data: bytes
    format: AudioFormat = AudioFormat.WAV
    duration: float = 0.0
    sample_rate: int = 22050
    voice_id: str = ""
    text: str = ""
    provider: str = ""
    processing_time: float = 0.0

    def save(self, path: Path | str) -> Path:
        """Save audio to file.

        Args:
            path: Output file path

        Returns:
            Path to the saved file
        """
        path = Path(path)
        path.write_bytes(self.audio_data)
        return path

    @property
    def size_bytes(self) -> int:
        """Get the size of audio data in bytes."""
        return len(self.audio_data)

    @property
    def size_kb(self) -> float:
        """Get the size of audio data in kilobytes."""
        return len(self.audio_data) / 1024

    def to_dict(self) -> dict:
        """Convert to dictionary (without audio data)."""
        return {
            "format": self.format.value,
            "duration": self.duration,
            "sample_rate": self.sample_rate,
            "voice_id": self.voice_id,
            "text": self.text,
            "provider": self.provider,
            "processing_time": self.processing_time,
            "size_bytes": self.size_bytes,
        }


@dataclass
class TTSConfig:
    """Configuration for text-to-speech synthesis.

    Attributes:
        voice: Voice ID to use (None for default)
        language: Language code (e.g., "en-US")
        rate: Speaking rate (0.5 = half speed, 2.0 = double speed)
        pitch: Voice pitch adjustment
        volume: Output volume (0.0 - 1.0)
        format: Output audio format
        sample_rate: Output sample rate
        style: Speaking style (if supported by voice)
        emotion: Emotion to convey (if supported)
    """

    voice: str | None = None
    language: str = "en-US"
    rate: float = 1.0
    pitch: float = 1.0
    volume: float = 1.0
    format: AudioFormat = AudioFormat.WAV
    sample_rate: int = 22050
    style: str | None = None
    emotion: str | None = None


@dataclass
class SSMLOptions:
    """SSML (Speech Synthesis Markup Language) options.

    Attributes:
        use_ssml: Whether to interpret input as SSML
        auto_breaks: Automatically add breaks at punctuation
        emphasis: Default emphasis level
        prosody: Prosody settings (rate, pitch, volume)
    """

    use_ssml: bool = False
    auto_breaks: bool = True
    emphasis: str = "moderate"
    prosody: dict = field(default_factory=dict)


__all__ = [
    "AudioFormat",
    "VoiceGender",
    "VoiceInfo",
    "SynthesisResult",
    "TTSConfig",
    "SSMLOptions",
]
