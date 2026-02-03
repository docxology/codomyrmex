"""Pyttsx3 text-to-speech provider for offline synthesis.

This provider uses pyttsx3 which provides offline TTS using:
- SAPI5 on Windows
- NSSpeechSynthesizer on macOS
- espeak on Linux

Advantages:
- Works completely offline
- No API keys required
- Fast synthesis
- Uses system voices
"""

import asyncio
import io
import tempfile
import time
from pathlib import Path
from typing import Optional

from codomyrmex.audio.exceptions import (
    ProviderNotAvailableError,
    SynthesisError,
    VoiceNotFoundError,
)

from ..models import (
    AudioFormat,
    SynthesisResult,
    TTSConfig,
    VoiceGender,
    VoiceInfo,
)
from .base import TTSProvider

# Check if pyttsx3 is available
try:
    import pyttsx3

    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    pyttsx3 = None  # type: ignore


class Pyttsx3Provider(TTSProvider):
    """Offline text-to-speech provider using pyttsx3.

    This provider works entirely offline using system TTS engines:
    - Windows: SAPI5
    - macOS: NSSpeechSynthesizer
    - Linux: espeak

    Example:
        ```python
        provider = Pyttsx3Provider()
        result = provider.synthesize("Hello world!")
        result.save("hello.wav")
        ```

    Attributes:
        name: Provider identifier
        is_available: Whether pyttsx3 is installed
    """

    name: str = "pyttsx3"
    is_available: bool = PYTTSX3_AVAILABLE

    def __init__(self, **kwargs: object) -> None:
        """Initialize the pyttsx3 provider.

        Raises:
            ProviderNotAvailableError: If pyttsx3 is not installed
        """
        if not PYTTSX3_AVAILABLE:
            raise ProviderNotAvailableError(
                "pyttsx3 is not installed. Install with: uv sync --extra audio",
                provider_name="pyttsx3",
                missing_packages=["pyttsx3"],
            )

        self._engine = pyttsx3.init()
        self._voices: list[VoiceInfo] = []
        self._load_voices()

    def _load_voices(self) -> None:
        """Load available voices from the system."""
        self._voices = []
        try:
            for voice in self._engine.getProperty("voices"):
                # Parse gender from voice properties
                gender = VoiceGender.UNKNOWN
                if hasattr(voice, "gender"):
                    gender_str = str(voice.gender).lower()
                    if "female" in gender_str or gender_str == "f":
                        gender = VoiceGender.FEMALE
                    elif "male" in gender_str or gender_str == "m":
                        gender = VoiceGender.MALE

                # Extract language from voice
                languages = getattr(voice, "languages", [])
                language = "en-US"
                if languages:
                    # Languages might be bytes or strings
                    lang = languages[0]
                    if isinstance(lang, bytes):
                        lang = lang.decode("utf-8", errors="ignore")
                    language = str(lang)

                self._voices.append(
                    VoiceInfo(
                        id=voice.id,
                        name=voice.name,
                        language=language,
                        gender=gender,
                        is_neural=False,
                        provider=self.name,
                        description=getattr(voice, "description", ""),
                    )
                )
        except Exception:
            # If we can't load voices, use a placeholder
            pass

    def synthesize(
        self,
        text: str,
        config: Optional[TTSConfig] = None,
    ) -> SynthesisResult:
        """Synthesize speech from text.

        Args:
            text: Text to synthesize
            config: Synthesis configuration options

        Returns:
            SynthesisResult with audio data (WAV format)

        Raises:
            SynthesisError: If synthesis fails
            VoiceNotFoundError: If requested voice is not available
        """
        if not text or not text.strip():
            raise SynthesisError("Cannot synthesize empty text")

        config = config or TTSConfig()
        start_time = time.time()

        try:
            # Set voice if specified
            if config.voice:
                voice_exists = any(v.id == config.voice for v in self._voices)
                if not voice_exists:
                    raise VoiceNotFoundError(
                        f"Voice not found: {config.voice}",
                        voice_id=config.voice,
                        available_voices=[v.id for v in self._voices[:10]],
                    )
                self._engine.setProperty("voice", config.voice)

            # Set rate (pyttsx3 uses words per minute, default ~200)
            base_rate = self._engine.getProperty("rate")
            self._engine.setProperty("rate", int(base_rate * config.rate))

            # Set volume (0.0 to 1.0)
            self._engine.setProperty("volume", config.volume)

            # Synthesize to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name

            self._engine.save_to_file(text, tmp_path)
            self._engine.runAndWait()

            # Read the audio data
            audio_path = Path(tmp_path)
            if not audio_path.exists():
                raise SynthesisError("Failed to generate audio file")

            audio_data = audio_path.read_bytes()

            # Calculate approximate duration (rough estimate)
            # WAV file size / (sample_rate * channels * bytes_per_sample)
            duration = len(audio_data) / (22050 * 1 * 2)  # Approximate

            # Clean up
            audio_path.unlink(missing_ok=True)

            # Reset rate
            self._engine.setProperty("rate", base_rate)

            processing_time = time.time() - start_time

            return SynthesisResult(
                audio_data=audio_data,
                format=AudioFormat.WAV,
                duration=duration,
                sample_rate=22050,
                voice_id=config.voice or self.default_voice,
                text=text,
                provider=self.name,
                processing_time=processing_time,
            )

        except (VoiceNotFoundError, SynthesisError):
            raise
        except Exception as e:
            raise SynthesisError(
                f"Synthesis failed: {e}",
                text=text,
                voice_id=config.voice,
            ) from e

    async def synthesize_async(
        self,
        text: str,
        config: Optional[TTSConfig] = None,
    ) -> SynthesisResult:
        """Synthesize speech asynchronously.

        Runs the synchronous synthesis in a thread pool.

        Args:
            text: Text to synthesize
            config: Synthesis configuration options

        Returns:
            SynthesisResult with audio data
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.synthesize(text, config),
        )

    def list_voices(
        self,
        language: Optional[str] = None,
    ) -> list[VoiceInfo]:
        """List available voices.

        Args:
            language: Filter by language code

        Returns:
            List of available VoiceInfo objects
        """
        if language:
            return [
                v for v in self._voices
                if v.language.lower().startswith(language.lower())
            ]
        return self._voices.copy()

    def get_voice(self, voice_id: str) -> Optional[VoiceInfo]:
        """Get information about a specific voice.

        Args:
            voice_id: Voice identifier

        Returns:
            VoiceInfo if found, None otherwise
        """
        for voice in self._voices:
            if voice.id == voice_id:
                return voice
        return None

    def get_supported_languages(self) -> list[str]:
        """Get list of supported language codes.

        Returns:
            List of unique language codes from available voices
        """
        languages = set()
        for voice in self._voices:
            languages.add(voice.language)
        return sorted(languages)

    @property
    def default_voice(self) -> str:
        """Get the default voice ID.

        Returns:
            Default voice identifier
        """
        if self._voices:
            return self._voices[0].id
        return ""


__all__ = ["Pyttsx3Provider", "PYTTSX3_AVAILABLE"]
