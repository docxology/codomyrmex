"""Data models for speech-to-text transcription.

This module defines the core data structures used for transcription results,
audio segments, word-level timing, and model configuration.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class WhisperModelSize(Enum):
    """Available Whisper model sizes.

    Larger models provide better accuracy but require more memory and
    processing time.

    Memory requirements (approximate):
    - TINY: ~1GB VRAM
    - BASE: ~1GB VRAM
    - SMALL: ~2GB VRAM
    - MEDIUM: ~5GB VRAM
    - LARGE: ~10GB VRAM
    - LARGE_V2: ~10GB VRAM
    - LARGE_V3: ~10GB VRAM
    """

    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    LARGE_V2 = "large-v2"
    LARGE_V3 = "large-v3"


@dataclass
class Word:
    """A single word with timing information.

    Attributes:
        word: The transcribed word text
        start: Start time in seconds
        end: End time in seconds
        probability: Confidence probability (0.0-1.0)
    """

    word: str
    start: float
    end: float
    probability: float = 1.0

    @property
    def duration(self) -> float:
        """Get the duration of the word in seconds."""
        return self.end - self.start


@dataclass
class Segment:
    """A transcription segment (typically a sentence or phrase).

    Attributes:
        id: Segment identifier (sequential)
        start: Start time in seconds
        end: End time in seconds
        text: Transcribed text for this segment
        words: Word-level timing information (if available)
        avg_logprob: Average log probability of tokens
        no_speech_prob: Probability that segment contains no speech
        compression_ratio: Text compression ratio
    """

    id: int
    start: float
    end: float
    text: str
    words: list[Word] = field(default_factory=list)
    avg_logprob: float = 0.0
    no_speech_prob: float = 0.0
    compression_ratio: float = 1.0

    @property
    def duration(self) -> float:
        """Get the duration of the segment in seconds."""
        return self.end - self.start

    def to_srt_format(self, index: int) -> str:
        """Format segment as SRT subtitle entry.

        Args:
            index: The subtitle index (1-based)

        Returns:
            SRT-formatted string for this segment
        """
        start_time = self._format_time_srt(self.start)
        end_time = self._format_time_srt(self.end)
        return f"{index}\n{start_time} --> {end_time}\n{self.text.strip()}\n"

    def to_vtt_format(self) -> str:
        """Format segment as VTT subtitle entry.

        Returns:
            VTT-formatted string for this segment
        """
        start_time = self._format_time_vtt(self.start)
        end_time = self._format_time_vtt(self.end)
        return f"{start_time} --> {end_time}\n{self.text.strip()}\n"

    @staticmethod
    def _format_time_srt(seconds: float) -> str:
        """Format time for SRT (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    @staticmethod
    def _format_time_vtt(seconds: float) -> str:
        """Format time for VTT (HH:MM:SS.mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


@dataclass
class TranscriptionResult:
    """Complete transcription result.

    Attributes:
        text: Full transcribed text
        segments: List of transcription segments with timing
        language: Detected or specified language code (ISO 639-1)
        language_probability: Confidence of language detection
        duration: Total audio duration in seconds
        processing_time: Time taken to transcribe in seconds
        model_size: Model size used for transcription
        source_path: Path to the source audio file
    """

    text: str
    segments: list[Segment] = field(default_factory=list)
    language: str = "en"
    language_probability: float = 1.0
    duration: float = 0.0
    processing_time: float = 0.0
    model_size: WhisperModelSize | None = None
    source_path: Path | None = None

    @property
    def word_count(self) -> int:
        """Get the total word count."""
        return len(self.text.split())

    @property
    def segment_count(self) -> int:
        """Get the number of segments."""
        return len(self.segments)

    def to_srt(self) -> str:
        """Export transcription as SRT subtitle format.

        Returns:
            Complete SRT-formatted subtitle string
        """
        lines = []
        for i, segment in enumerate(self.segments, start=1):
            lines.append(segment.to_srt_format(i))
        return "\n".join(lines)

    def to_vtt(self) -> str:
        """Export transcription as WebVTT subtitle format.

        Returns:
            Complete VTT-formatted subtitle string
        """
        lines = ["WEBVTT\n"]
        for segment in self.segments:
            lines.append(segment.to_vtt_format())
        return "\n".join(lines)

    def to_txt(self) -> str:
        """Export transcription as plain text.

        Returns:
            Plain text transcription
        """
        return self.text

    def to_json(self) -> dict:
        """Export transcription as JSON-serializable dictionary.

        Returns:
            Dictionary with all transcription data
        """
        return {
            "text": self.text,
            "language": self.language,
            "language_probability": self.language_probability,
            "duration": self.duration,
            "processing_time": self.processing_time,
            "model_size": self.model_size.value if self.model_size else None,
            "source_path": str(self.source_path) if self.source_path else None,
            "segments": [
                {
                    "id": s.id,
                    "start": s.start,
                    "end": s.end,
                    "text": s.text,
                    "avg_logprob": s.avg_logprob,
                    "no_speech_prob": s.no_speech_prob,
                    "words": [
                        {
                            "word": w.word,
                            "start": w.start,
                            "end": w.end,
                            "probability": w.probability,
                        }
                        for w in s.words
                    ],
                }
                for s in self.segments
            ],
        }

    def save_srt(self, path: Path | str) -> Path:
        """Save transcription as SRT file.

        Args:
            path: Output file path

        Returns:
            Path to the saved file
        """
        path = Path(path)
        path.write_text(self.to_srt(), encoding="utf-8")
        return path

    def save_vtt(self, path: Path | str) -> Path:
        """Save transcription as VTT file.

        Args:
            path: Output file path

        Returns:
            Path to the saved file
        """
        path = Path(path)
        path.write_text(self.to_vtt(), encoding="utf-8")
        return path


@dataclass
class TranscriptionConfig:
    """Configuration for transcription operations.

    Attributes:
        language: Language code (None for auto-detection)
        task: Task type - "transcribe" or "translate"
        beam_size: Beam size for decoding (higher = more accurate, slower)
        best_of: Number of candidates to generate
        patience: Beam search patience factor
        temperature: Sampling temperature
        compression_ratio_threshold: Skip segments with high compression
        log_prob_threshold: Skip segments with low log probability
        no_speech_threshold: Skip segments with high no-speech probability
        word_timestamps: Enable word-level timestamps
        vad_filter: Enable voice activity detection filtering
        vad_parameters: VAD filter parameters
    """

    language: str | None = None
    task: str = "transcribe"
    beam_size: int = 5
    best_of: int = 5
    patience: float = 1.0
    temperature: float | tuple[float, ...] = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
    compression_ratio_threshold: float = 2.4
    log_prob_threshold: float = -1.0
    no_speech_threshold: float = 0.6
    word_timestamps: bool = True
    vad_filter: bool = True
    vad_parameters: dict | None = None


__all__ = [
    "WhisperModelSize",
    "Word",
    "Segment",
    "TranscriptionResult",
    "TranscriptionConfig",
]
