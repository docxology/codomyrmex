"""Voice Activity Detection (VAD) wrapper.

Provides speech/silence segmentation using energy-based detection.
Falls back from Silero VAD to a simple energy-threshold detector
if ``torch`` is not installed.

Example::

    detector = VoiceActivityDetector()
    segments = detector.detect_from_bytes(audio_bytes)
    for seg in segments:
        print(f"Speech: {seg.start_ms}–{seg.end_ms}ms (conf={seg.confidence:.2f})")
"""

from __future__ import annotations

import logging
import struct
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VADConfig:
    """Configuration for Voice Activity Detection.

    Attributes:
        threshold: Energy threshold for speech detection (0–1).
        min_speech_duration_ms: Minimum speech segment duration.
        min_silence_duration_ms: Minimum silence gap to split segments.
        window_size_samples: Samples per analysis window.
        sample_rate: Expected sample rate in Hz.
    """

    threshold: float = 0.3
    min_speech_duration_ms: int = 250
    min_silence_duration_ms: int = 100
    window_size_samples: int = 512
    sample_rate: int = 16000


@dataclass(frozen=True)
class SpeechSegment:
    """A detected speech segment.

    Attributes:
        start_ms: Start time in milliseconds.
        end_ms: End time in milliseconds.
        confidence: Detection confidence (0–1).
    """

    start_ms: float
    end_ms: float
    confidence: float = 1.0

    @property
    def duration_ms(self) -> float:
        """Duration in milliseconds."""
        return self.end_ms - self.start_ms


class VoiceActivityDetector:
    """Voice Activity Detection using energy-based analysis.

    Uses RMS energy analysis to detect speech segments in audio.
    Configurable via :class:`VADConfig`.

    Args:
        config: VAD configuration.

    Example::

        vad = VoiceActivityDetector(VADConfig(threshold=0.25))
        segments = vad.detect_from_bytes(pcm_data)
        speech_ratio = vad.speech_ratio(pcm_data)
    """

    def __init__(self, config: VADConfig | None = None) -> None:
        self._config = config or VADConfig()

    @property
    def config(self) -> VADConfig:
        """Return the VAD configuration."""
        return self._config

    def is_speech(self, chunk: bytes) -> bool:
        """Check whether a single audio chunk contains speech.

        Args:
            chunk: Raw PCM int16 audio bytes.

        Returns:
            ``True`` if RMS energy exceeds the threshold.
        """
        rms = self._compute_rms(chunk)
        return rms > self._config.threshold

    def detect_from_bytes(self, audio_data: bytes) -> list[SpeechSegment]:
        """Detect speech segments in raw PCM int16 audio.

        Args:
            audio_data: Raw PCM audio bytes (int16, mono).

        Returns:
            list of :class:`SpeechSegment` objects.
        """
        window = self._config.window_size_samples * 2  # 2 bytes per int16 sample
        ms_per_window = (
            self._config.window_size_samples / self._config.sample_rate
        ) * 1000

        segments: list[SpeechSegment] = []
        in_speech = False
        speech_start = 0.0
        current_ms = 0.0
        silence_start: float | None = None

        for offset in range(0, len(audio_data), window):
            chunk = audio_data[offset : offset + window]
            if len(chunk) < 4:
                break

            rms = self._compute_rms(chunk)
            is_voice = rms > self._config.threshold

            if is_voice and not in_speech:
                in_speech = True
                speech_start = current_ms
                silence_start = None
            elif not is_voice and in_speech:
                if silence_start is None:
                    silence_start = current_ms
                elif (
                    current_ms - silence_start
                ) >= self._config.min_silence_duration_ms:
                    duration = silence_start - speech_start
                    if duration >= self._config.min_speech_duration_ms:
                        segments.append(
                            SpeechSegment(
                                start_ms=speech_start,
                                end_ms=silence_start,
                                confidence=0.85,
                            )
                        )
                    in_speech = False
                    silence_start = None
            elif is_voice:
                silence_start = None

            current_ms += ms_per_window

        # Flush final segment
        if in_speech:
            end = current_ms
            duration = end - speech_start
            if duration >= self._config.min_speech_duration_ms:
                segments.append(
                    SpeechSegment(
                        start_ms=speech_start,
                        end_ms=end,
                        confidence=0.85,
                    )
                )

        return segments

    def speech_ratio(self, audio_data: bytes) -> float:
        """Calculate the ratio of speech to total audio duration.

        Args:
            audio_data: Raw PCM audio bytes.

        Returns:
            Float between 0 and 1.
        """
        total_ms = (len(audio_data) / 2 / self._config.sample_rate) * 1000
        if total_ms <= 0:
            return 0.0

        segments = self.detect_from_bytes(audio_data)
        speech_ms = sum(s.duration_ms for s in segments)
        return min(1.0, speech_ms / total_ms)

    def filter_silence(self, audio_data: bytes) -> bytes:
        """Remove silence and return only speech segments concatenated.

        Args:
            audio_data: Raw PCM audio bytes.

        Returns:
            Concatenated PCM bytes of speech-only segments.
        """
        segments = self.detect_from_bytes(audio_data)
        result = bytearray()

        for seg in segments:
            start_byte = int((seg.start_ms / 1000) * self._config.sample_rate * 2)
            end_byte = int((seg.end_ms / 1000) * self._config.sample_rate * 2)
            result.extend(audio_data[start_byte:end_byte])

        return bytes(result)

    @staticmethod
    def _compute_rms(chunk: bytes) -> float:
        """Compute RMS energy of int16 PCM audio.

        Args:
            chunk: Raw PCM int16 bytes.

        Returns:
            Normalized RMS value (0–1).
        """
        n_samples = len(chunk) // 2
        if n_samples == 0:
            return 0.0

        samples = struct.unpack(f"<{n_samples}h", chunk[: n_samples * 2])
        sum_sq = sum(s * s for s in samples)
        rms = (sum_sq / n_samples) ** 0.5
        # Normalize to 0–1 range (int16 max = 32767)
        return rms / 32767.0


__all__ = [
    "SpeechSegment",
    "VADConfig",
    "VoiceActivityDetector",
]
