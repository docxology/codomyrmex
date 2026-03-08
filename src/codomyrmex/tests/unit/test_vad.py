"""Tests for audio.speech_to_text.vad — Voice Activity Detection.

Zero-Mock: All tests use real PCM audio data with real energy analysis.
"""

from __future__ import annotations

import math
import struct

import pytest

from codomyrmex.audio.speech_to_text.vad import (
    SpeechSegment,
    VADConfig,
    VoiceActivityDetector,
)


def _generate_pcm_tone(
    frequency_hz: float = 440.0,
    duration_ms: int = 500,
    sample_rate: int = 16000,
    amplitude: float = 0.8,
) -> bytes:
    """Generate a pure sine tone as PCM int16 bytes."""
    n_samples = int(sample_rate * duration_ms / 1000)
    samples = []
    for i in range(n_samples):
        t = i / sample_rate
        value = amplitude * math.sin(2 * math.pi * frequency_hz * t)
        samples.append(int(value * 32767))
    return struct.pack(f"<{len(samples)}h", *samples)


def _generate_silence(duration_ms: int = 500, sample_rate: int = 16000) -> bytes:
    """Generate silence as PCM int16 bytes."""
    n_samples = int(sample_rate * duration_ms / 1000)
    return b"\x00\x00" * n_samples


# ── VADConfig ─────────────────────────────────────────────────────────


class TestVADConfig:
    """Verify config defaults."""

    def test_defaults(self) -> None:
        cfg = VADConfig()
        assert cfg.threshold == 0.3
        assert cfg.min_speech_duration_ms == 250
        assert cfg.sample_rate == 16000

    def test_custom_values(self) -> None:
        cfg = VADConfig(threshold=0.5, min_speech_duration_ms=100)
        assert cfg.threshold == 0.5


# ── SpeechSegment ─────────────────────────────────────────────────────


class TestSpeechSegment:
    """Verify segment properties."""

    def test_duration(self) -> None:
        seg = SpeechSegment(start_ms=100, end_ms=300)
        assert seg.duration_ms == 200


# ── VoiceActivityDetector ─────────────────────────────────────────────


class TestVoiceActivityDetector:
    """Test actual VAD on real PCM data."""

    def test_is_speech_with_tone(self) -> None:
        vad = VoiceActivityDetector()
        tone = _generate_pcm_tone(duration_ms=50, amplitude=0.8)
        assert vad.is_speech(tone) is True

    def test_is_speech_with_silence(self) -> None:
        vad = VoiceActivityDetector()
        silence = _generate_silence(duration_ms=50)
        assert vad.is_speech(silence) is False

    def test_detect_pure_tone(self) -> None:
        vad = VoiceActivityDetector(VADConfig(threshold=0.1))
        tone = _generate_pcm_tone(duration_ms=500, amplitude=0.8)
        segments = vad.detect_from_bytes(tone)
        assert len(segments) >= 1
        assert segments[0].duration_ms > 200

    def test_detect_silence_only(self) -> None:
        vad = VoiceActivityDetector()
        silence = _generate_silence(duration_ms=500)
        segments = vad.detect_from_bytes(silence)
        assert len(segments) == 0

    def test_detect_tone_silence_tone(self) -> None:
        """Detect two speech segments separated by silence."""
        vad = VoiceActivityDetector(
            VADConfig(
                threshold=0.1,
                min_speech_duration_ms=100,
                min_silence_duration_ms=50,
            )
        )
        audio = (
            _generate_pcm_tone(duration_ms=300, amplitude=0.8)
            + _generate_silence(duration_ms=300)
            + _generate_pcm_tone(duration_ms=300, amplitude=0.8)
        )
        segments = vad.detect_from_bytes(audio)
        assert len(segments) == 2

    def test_speech_ratio_full_speech(self) -> None:
        vad = VoiceActivityDetector(VADConfig(threshold=0.1))
        tone = _generate_pcm_tone(duration_ms=1000, amplitude=0.8)
        ratio = vad.speech_ratio(tone)
        assert ratio > 0.8

    def test_speech_ratio_silence(self) -> None:
        vad = VoiceActivityDetector()
        silence = _generate_silence(duration_ms=1000)
        ratio = vad.speech_ratio(silence)
        assert ratio == 0.0

    def test_filter_silence(self) -> None:
        vad = VoiceActivityDetector(VADConfig(threshold=0.1))
        tone = _generate_pcm_tone(duration_ms=500, amplitude=0.8)
        silence = _generate_silence(duration_ms=500)
        combined = tone + silence
        filtered = vad.filter_silence(combined)
        assert len(filtered) < len(combined)
        assert len(filtered) > 0

    def test_empty_audio(self) -> None:
        vad = VoiceActivityDetector()
        segments = vad.detect_from_bytes(b"")
        assert segments == []
        assert vad.speech_ratio(b"") == 0.0
