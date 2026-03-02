"""Edge TTS provider for neural text-to-speech.

This provider uses Microsoft Edge's online TTS service via the edge-tts library.
It provides access to 300+ neural voices across many languages, completely free.

Advantages:
- High-quality neural voices
- 300+ voices in 40+ languages
- Completely free (no API key needed)
- SSML support for fine-grained control

Requirements:
- Internet connection
- edge-tts package
"""

import asyncio
import time
from pathlib import Path

from codomyrmex.audio.exceptions import (
    ProviderNotAvailableError,
    SynthesisError,
    VoiceNotFoundError,
)
from codomyrmex.audio.text_to_speech.models import (
    AudioFormat,
    SynthesisResult,
    TTSConfig,
    VoiceGender,
    VoiceInfo,
)

from .base import TTSProvider

# Check if edge-tts is available
try:
    import edge_tts

    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    edge_tts = None  # type: ignore


class EdgeTTSProvider(TTSProvider):
    """Neural text-to-speech provider using Microsoft Edge TTS.

    This provider offers high-quality neural TTS voices through Microsoft's
    Edge TTS service. It's free to use but requires an internet connection.

    Example:
        ```python
        provider = EdgeTTSProvider()
        result = await provider.synthesize_async("Hello world!",
            TTSConfig(voice="en-US-AriaNeural"))
        result.save("hello.mp3")
        ```

    Popular voices:
    - en-US-AriaNeural (Female, US English)
    - en-US-GuyNeural (Male, US English)
    - en-GB-SoniaNeural (Female, British English)
    - es-ES-ElviraNeural (Female, Spanish)
    - fr-FR-DeniseNeural (Female, French)
    - de-DE-KatjaNeural (Female, German)
    - ja-JP-NanamiNeural (Female, Japanese)
    - zh-CN-XiaoxiaoNeural (Female, Chinese)

    Attributes:
        name: Provider identifier
        is_available: Whether edge-tts is installed
    """

    name: str = "edge-tts"
    is_available: bool = EDGE_TTS_AVAILABLE

    def __init__(self, **kwargs: object) -> None:
        """Initialize the Edge TTS provider.

        Raises:
            ProviderNotAvailableError: If edge-tts is not installed
        """
        if not EDGE_TTS_AVAILABLE:
            raise ProviderNotAvailableError(
                "edge-tts is not installed. Install with: uv sync --extra audio",
                provider_name="edge-tts",
                missing_packages=["edge-tts"],
            )

        self._voices: list[VoiceInfo] = []
        self._voices_loaded = False

    async def _load_voices(self) -> None:
        """Load available voices from Edge TTS service."""
        if self._voices_loaded:
            return

        try:
            voices = await edge_tts.list_voices()
            self._voices = []

            for voice in voices:
                # Parse gender
                gender = VoiceGender.UNKNOWN
                gender_str = voice.get("Gender", "").lower()
                if gender_str == "female":
                    gender = VoiceGender.FEMALE
                elif gender_str == "male":
                    gender = VoiceGender.MALE

                # Parse styles if available
                styles = []
                style_list = voice.get("VoiceTag", {}).get("ContentCategories", [])
                if style_list:
                    styles = style_list

                self._voices.append(
                    VoiceInfo(
                        id=voice["ShortName"],
                        name=voice["FriendlyName"],
                        language=voice.get("Locale", "en-US"),
                        gender=gender,
                        is_neural=True,  # All Edge TTS voices are neural
                        provider=self.name,
                        description=voice.get("FriendlyName", ""),
                        sample_rate=24000,  # Edge TTS outputs 24kHz
                        styles=styles,
                    )
                )

            self._voices_loaded = True
        except Exception as e:
            raise SynthesisError(f"Failed to load voices: {e}") from e

    def synthesize(
        self,
        text: str,
        config: TTSConfig | None = None,
    ) -> SynthesisResult:
        """Synthesize speech from text (synchronous wrapper).

        Args:
            text: Text to synthesize
            config: Synthesis configuration options

        Returns:
            SynthesisResult with audio data
        """
        return asyncio.get_event_loop().run_until_complete(
            self.synthesize_async(text, config)
        )

    async def synthesize_async(
        self,
        text: str,
        config: TTSConfig | None = None,
    ) -> SynthesisResult:
        """Synthesize speech from text asynchronously.

        Args:
            text: Text to synthesize
            config: Synthesis configuration options

        Returns:
            SynthesisResult with audio data (MP3 format)

        Raises:
            SynthesisError: If synthesis fails
            VoiceNotFoundError: If requested voice is not available
        """
        if not text or not text.strip():
            raise SynthesisError("Cannot synthesize empty text")

        config = config or TTSConfig()
        start_time = time.time()

        # Load voices if not already loaded
        await self._load_voices()

        # Get voice
        voice = config.voice or self.default_voice
        if voice and self._voices:
            voice_exists = any(v.id == voice for v in self._voices)
            if not voice_exists:
                raise VoiceNotFoundError(
                    f"Voice not found: {voice}",
                    voice_id=voice,
                    available_voices=[v.id for v in self._voices[:10]],
                )

        try:
            # Build rate and pitch strings
            # Edge TTS uses percentage format: "+50%" or "-25%"
            rate_pct = int((config.rate - 1.0) * 100)
            rate_str = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"

            pitch_pct = int((config.pitch - 1.0) * 50)  # pitch is more sensitive
            pitch_str = f"+{pitch_pct}Hz" if pitch_pct >= 0 else f"{pitch_pct}Hz"

            # Create communicate instance
            communicate = edge_tts.Communicate(
                text,
                voice=voice,
                rate=rate_str,
                pitch=pitch_str,
            )

            # Collect audio data
            audio_chunks: list[bytes] = []

            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_chunks.append(chunk["data"])

            if not audio_chunks:
                raise SynthesisError("No audio data generated")

            audio_data = b"".join(audio_chunks)

            # Estimate duration (MP3 at ~128kbps)
            duration = len(audio_data) / (128 * 1024 / 8)  # Rough estimate

            processing_time = time.time() - start_time

            return SynthesisResult(
                audio_data=audio_data,
                format=AudioFormat.MP3,
                duration=duration,
                sample_rate=24000,
                voice_id=voice,
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
                voice_id=voice,
            ) from e

    async def synthesize_to_file_async(
        self,
        text: str,
        output_path: str | Path,
        config: TTSConfig | None = None,
    ) -> Path:
        """Synthesize speech directly to a file.

        This is more efficient for large text as it streams directly to disk.

        Args:
            text: Text to synthesize
            output_path: Output file path
            config: Synthesis configuration options

        Returns:
            Path to the saved file
        """
        config = config or TTSConfig()
        output_path = Path(output_path)

        voice = config.voice or self.default_voice

        rate_pct = int((config.rate - 1.0) * 100)
        rate_str = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"

        communicate = edge_tts.Communicate(
            text,
            voice=voice,
            rate=rate_str,
        )

        await communicate.save(str(output_path))
        return output_path

    def list_voices(
        self,
        language: str | None = None,
    ) -> list[VoiceInfo]:
        """List available voices.

        Args:
            language: Filter by language code (e.g., "en-US" or "en")

        Returns:
            List of available VoiceInfo objects
        """
        # Ensure voices are loaded
        if not self._voices_loaded:
            asyncio.get_event_loop().run_until_complete(self._load_voices())

        if language:
            return [
                v for v in self._voices
                if v.language.lower().startswith(language.lower())
            ]
        return self._voices.copy()

    async def list_voices_async(
        self,
        language: str | None = None,
    ) -> list[VoiceInfo]:
        """List available voices asynchronously.

        Args:
            language: Filter by language code

        Returns:
            List of available VoiceInfo objects
        """
        await self._load_voices()

        if language:
            return [
                v for v in self._voices
                if v.language.lower().startswith(language.lower())
            ]
        return self._voices.copy()

    def get_voice(self, voice_id: str) -> VoiceInfo | None:
        """Get information about a specific voice.

        Args:
            voice_id: Voice identifier (e.g., "en-US-AriaNeural")

        Returns:
            VoiceInfo if found, None otherwise
        """
        if not self._voices_loaded:
            asyncio.get_event_loop().run_until_complete(self._load_voices())

        for voice in self._voices:
            if voice.id == voice_id:
                return voice
        return None

    def get_supported_languages(self) -> list[str]:
        """Get list of supported language codes.

        Returns:
            List of unique language codes
        """
        if not self._voices_loaded:
            asyncio.get_event_loop().run_until_complete(self._load_voices())

        languages = set()
        for voice in self._voices:
            languages.add(voice.language)
        return sorted(languages)

    @property
    def default_voice(self) -> str:
        """Get the default voice ID.

        Returns:
            Default voice identifier (en-US-AriaNeural)
        """
        return "en-US-AriaNeural"


# Common Edge TTS voices for convenience
POPULAR_VOICES = {
    "en-US": ["en-US-AriaNeural", "en-US-GuyNeural", "en-US-JennyNeural"],
    "en-GB": ["en-GB-SoniaNeural", "en-GB-RyanNeural"],
    "es-ES": ["es-ES-ElviraNeural", "es-ES-AlvaroNeural"],
    "fr-FR": ["fr-FR-DeniseNeural", "fr-FR-HenriNeural"],
    "de-DE": ["de-DE-KatjaNeural", "de-DE-ConradNeural"],
    "it-IT": ["it-IT-ElsaNeural", "it-IT-DiegoNeural"],
    "pt-BR": ["pt-BR-FranciscaNeural", "pt-BR-AntonioNeural"],
    "ja-JP": ["ja-JP-NanamiNeural", "ja-JP-KeitaNeural"],
    "ko-KR": ["ko-KR-SunHiNeural", "ko-KR-InJoonNeural"],
    "zh-CN": ["zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural"],
}


__all__ = ["EdgeTTSProvider", "EDGE_TTS_AVAILABLE", "POPULAR_VOICES"]
