"""Whisper speech-to-text provider using faster-whisper.

This provider uses the faster-whisper library which implements Whisper
using CTranslate2 for efficient inference. It provides:
- 4x faster transcription than original Whisper
- Lower memory usage
- Word-level timestamps
- Voice activity detection (VAD) filtering
- Support for 99+ languages
"""

import asyncio
import time
from pathlib import Path
from collections.abc import AsyncIterator

from codomyrmex.audio.exceptions import (
    AudioFormatError,
    ModelNotLoadedError,
    ProviderNotAvailableError,
    TranscriptionError,
)

from ..models import (
    Segment,
    TranscriptionConfig,
    TranscriptionResult,
    WhisperModelSize,
    Word,
)
from .base import STTProvider

# Check if faster-whisper is available
try:
    from faster_whisper import WhisperModel

    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False
    WhisperModel = None  # type: ignore


# Supported audio formats
SUPPORTED_FORMATS = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".webm", ".mp4", ".mpeg", ".mpga", ".oga", ".opus"}

# Language codes supported by Whisper
WHISPER_LANGUAGES = [
    "af", "am", "ar", "as", "az", "ba", "be", "bg", "bn", "bo", "br", "bs", "ca", "cs",
    "cy", "da", "de", "el", "en", "es", "et", "eu", "fa", "fi", "fo", "fr", "gl", "gu",
    "ha", "haw", "he", "hi", "hr", "ht", "hu", "hy", "id", "is", "it", "ja", "jw", "ka",
    "kk", "km", "kn", "ko", "la", "lb", "ln", "lo", "lt", "lv", "mg", "mi", "mk", "ml",
    "mn", "mr", "ms", "mt", "my", "ne", "nl", "nn", "no", "oc", "pa", "pl", "ps", "pt",
    "ro", "ru", "sa", "sd", "si", "sk", "sl", "sn", "so", "sq", "sr", "su", "sv", "sw",
    "ta", "te", "tg", "th", "tk", "tl", "tr", "tt", "uk", "ur", "uz", "vi", "yi", "yo",
    "zh", "yue",
]


class WhisperProvider(STTProvider):
    """Speech-to-text provider using faster-whisper.

    This provider offers efficient local transcription using Whisper models
    accelerated with CTranslate2.

    Example:
        ```python
        provider = WhisperProvider(model_size=WhisperModelSize.BASE)
        result = provider.transcribe("audio.mp3")
        print(result.text)
        ```

    Attributes:
        name: Provider identifier
        model_size: Current model size
        device: Compute device being used
    """

    name: str = "whisper"
    is_available: bool = FASTER_WHISPER_AVAILABLE

    def __init__(
        self,
        model_size: WhisperModelSize = WhisperModelSize.BASE,
        device: str = "auto",
        compute_type: str = "auto",
        download_root: str | None = None,
        local_files_only: bool = False,
        **kwargs: object,
    ) -> None:
        """Initialize the Whisper provider.

        Args:
            model_size: Size of the Whisper model to use
            device: Device to run on ("auto", "cpu", "cuda")
            compute_type: Computation type ("auto", "float16", "int8", "float32")
            download_root: Directory to store downloaded models
            local_files_only: Only use locally cached models
            **kwargs: Additional arguments passed to WhisperModel

        Raises:
            ProviderNotAvailableError: If faster-whisper is not installed
        """
        if not FASTER_WHISPER_AVAILABLE:
            raise ProviderNotAvailableError(
                "faster-whisper is not installed. Install with: uv sync --extra audio",
                provider_name="whisper",
                missing_packages=["faster-whisper"],
            )

        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._download_root = download_root
        self._local_files_only = local_files_only
        self._model: WhisperModel | None = None
        self._kwargs = kwargs

        # Load model immediately
        self._load_model()

    def _load_model(self) -> None:
        """Load the Whisper model."""
        try:
            self._model = WhisperModel(
                self.model_size.value,
                device=self.device,
                compute_type=self.compute_type,
                download_root=self._download_root,
                local_files_only=self._local_files_only,
            )
        except Exception as e:
            raise ModelNotLoadedError(
                f"Failed to load Whisper model: {e}",
                model_name="whisper",
                model_size=self.model_size.value,
            ) from e

    def _validate_audio_path(self, audio_path: str | Path) -> Path:
        """Validate the audio file path.

        Args:
            audio_path: Path to validate

        Returns:
            Validated Path object

        Raises:
            TranscriptionError: If file doesn't exist
            AudioFormatError: If format is not supported
        """
        path = Path(audio_path)

        if not path.exists():
            raise TranscriptionError(
                f"Audio file not found: {path}",
                audio_path=path,
            )

        if path.suffix.lower() not in SUPPORTED_FORMATS:
            raise AudioFormatError(
                f"Unsupported audio format: {path.suffix}",
                format_type=path.suffix,
                supported_formats=list(SUPPORTED_FORMATS),
            )

        return path

    def transcribe(
        self,
        audio_path: str | Path,
        config: TranscriptionConfig | None = None,
    ) -> TranscriptionResult:
        """Transcribe an audio file.

        Args:
            audio_path: Path to the audio file
            config: Transcription configuration options

        Returns:
            TranscriptionResult with text, segments, and metadata

        Raises:
            TranscriptionError: If transcription fails
            ModelNotLoadedError: If model is not loaded
        """
        if not self._model:
            raise ModelNotLoadedError(
                "Whisper model not loaded",
                model_name="whisper",
                model_size=self.model_size.value,
            )

        path = self._validate_audio_path(audio_path)
        config = config or TranscriptionConfig()

        start_time = time.time()

        try:
            # Build transcription parameters
            params = {
                "language": config.language,
                "task": config.task,
                "beam_size": config.beam_size,
                "best_of": config.best_of,
                "patience": config.patience,
                "temperature": config.temperature,
                "compression_ratio_threshold": config.compression_ratio_threshold,
                "log_prob_threshold": config.log_prob_threshold,
                "no_speech_threshold": config.no_speech_threshold,
                "word_timestamps": config.word_timestamps,
                "vad_filter": config.vad_filter,
            }

            if config.vad_parameters:
                params["vad_parameters"] = config.vad_parameters

            # Perform transcription
            segments_gen, info = self._model.transcribe(str(path), **params)

            # Collect segments
            segments: list[Segment] = []
            all_text: list[str] = []

            for i, seg in enumerate(segments_gen):
                words: list[Word] = []
                if seg.words:
                    for w in seg.words:
                        words.append(
                            Word(
                                word=w.word,
                                start=w.start,
                                end=w.end,
                                probability=w.probability,
                            )
                        )

                segment = Segment(
                    id=i,
                    start=seg.start,
                    end=seg.end,
                    text=seg.text,
                    words=words,
                    avg_logprob=seg.avg_logprob,
                    no_speech_prob=seg.no_speech_prob,
                    compression_ratio=seg.compression_ratio,
                )
                segments.append(segment)
                all_text.append(seg.text)

            processing_time = time.time() - start_time

            return TranscriptionResult(
                text=" ".join(all_text).strip(),
                segments=segments,
                language=info.language,
                language_probability=info.language_probability,
                duration=info.duration,
                processing_time=processing_time,
                model_size=self.model_size,
                source_path=path,
            )

        except Exception as e:
            if isinstance(e, (TranscriptionError, AudioFormatError, ModelNotLoadedError)):
                raise
            raise TranscriptionError(
                f"Transcription failed: {e}",
                audio_path=path,
                language=config.language,
                model_size=self.model_size.value,
            ) from e

    async def transcribe_async(
        self,
        audio_path: str | Path,
        config: TranscriptionConfig | None = None,
    ) -> TranscriptionResult:
        """Transcribe an audio file asynchronously.

        This runs the synchronous transcription in a thread pool to avoid
        blocking the event loop.

        Args:
            audio_path: Path to the audio file
            config: Transcription configuration options

        Returns:
            TranscriptionResult with text and segments
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.transcribe(audio_path, config),
        )

    async def transcribe_stream(
        self,
        audio_path: str | Path,
        config: TranscriptionConfig | None = None,
    ) -> AsyncIterator[TranscriptionResult]:
        """Stream transcription results as segments complete.

        Args:
            audio_path: Path to the audio file
            config: Transcription configuration options

        Yields:
            Partial TranscriptionResult with accumulated segments
        """
        if not self._model:
            raise ModelNotLoadedError(
                "Whisper model not loaded",
                model_name="whisper",
                model_size=self.model_size.value,
            )

        path = self._validate_audio_path(audio_path)
        config = config or TranscriptionConfig()

        start_time = time.time()

        params = {
            "language": config.language,
            "task": config.task,
            "beam_size": config.beam_size,
            "word_timestamps": config.word_timestamps,
            "vad_filter": config.vad_filter,
        }

        segments_gen, info = self._model.transcribe(str(path), **params)

        segments: list[Segment] = []
        all_text: list[str] = []

        for i, seg in enumerate(segments_gen):
            words: list[Word] = []
            if seg.words:
                for w in seg.words:
                    words.append(
                        Word(
                            word=w.word,
                            start=w.start,
                            end=w.end,
                            probability=w.probability,
                        )
                    )

            segment = Segment(
                id=i,
                start=seg.start,
                end=seg.end,
                text=seg.text,
                words=words,
                avg_logprob=seg.avg_logprob,
                no_speech_prob=seg.no_speech_prob,
            )
            segments.append(segment)
            all_text.append(seg.text)

            # Yield partial result
            yield TranscriptionResult(
                text=" ".join(all_text).strip(),
                segments=segments.copy(),
                language=info.language,
                language_probability=info.language_probability,
                duration=info.duration,
                processing_time=time.time() - start_time,
                model_size=self.model_size,
                source_path=path,
            )

            # Allow other tasks to run
            await asyncio.sleep(0)

    def detect_language(
        self,
        audio_path: str | Path,
    ) -> tuple[str, float]:
        """Detect the language of an audio file.

        Only the first 30 seconds of audio are used for detection.

        Args:
            audio_path: Path to the audio file

        Returns:
            Tuple of (language_code, probability)
        """
        if not self._model:
            raise ModelNotLoadedError(
                "Whisper model not loaded",
                model_name="whisper",
            )

        path = self._validate_audio_path(audio_path)

        try:
            # Use short transcription to detect language
            _, info = self._model.transcribe(
                str(path),
                language=None,
                task="transcribe",
            )
            return info.language, info.language_probability
        except Exception as e:
            raise TranscriptionError(
                f"Language detection failed: {e}",
                audio_path=path,
            ) from e

    def get_supported_languages(self) -> list[str]:
        """Get list of supported language codes.

        Returns:
            List of ISO 639-1 language codes supported by Whisper
        """
        return WHISPER_LANGUAGES.copy()

    @property
    def is_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self._model is not None

    def unload(self) -> None:
        """Unload the model to free memory."""
        if self._model is not None:
            del self._model
            self._model = None


__all__ = ["WhisperProvider", "WHISPER_LANGUAGES", "SUPPORTED_FORMATS"]
