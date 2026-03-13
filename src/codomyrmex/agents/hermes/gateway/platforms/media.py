"""Hermes Gateway Multimodal Media Handlers.

Provides extraction pipelines for Voice, Images, and Documents bridging into LLM contexts.
"""

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class AudioTranscriber:
    """Wrapper for native audio transcription of raw channel payloads."""

    def __init__(self) -> None:
        """Initialize transcriber dependencies."""
        # Defer import to prevent slow initializations when not strictly needed
        from codomyrmex.audio import Transcriber, WhisperModelSize

        self._processor = Transcriber(model_size=WhisperModelSize.BASE)

    async def transcribe_bytes(
        self, audio_bytes: bytes, filename: str = "audio.wav"
    ) -> str:
        """Transcribe raw audio bytes into text.

        Args:
            audio_bytes: The raw byte payload of the voice note.
            filename: Original or inferred filename/extension.

        Returns:
            The transcribed text.
        """
        import asyncio
        import os
        import tempfile

        # We write to a temporary file since most native audio transcribers
        # (like Whisper via ffmpeg) prefer disk files to resolve arbitrary containers (ogg/mp4/etc).
        _, ext = os.path.splitext(filename)
        if not ext:
            ext = ".wav"

        fd, temp_path = tempfile.mkstemp(suffix=ext, prefix="hermes_audio_")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(audio_bytes)

            logger.info(
                f"Transcribing audio payload {len(audio_bytes)} bytes resolving natively."
            )

            # Using asyncio.to_thread because the underlying Transcriber.transcribe
            # might run synchronous ML inference blocking the gateway event loop.
            result = await asyncio.to_thread(self._processor.transcribe, temp_path)

            return result.text
        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            raise
        finally:
            try:
                os.remove(temp_path)
            except OSError:
                pass


class VisionAnalyzer:
    """Wrapper for native local VLM image description of raw channel payloads."""

    def __init__(self, model: str = "llama3.2-vision") -> None:
        """Initialize vision dependencies."""
        # Defer import to prevent slow initializations when not strictly needed
        from codomyrmex.vision import VLMClient, VLMConfig

        self._config = VLMConfig(model_name=model)
        self._client = VLMClient(config=self._config)

    async def describe_image(
        self, image_bytes: bytes, filename: str = "image.png"
    ) -> str:
        """Analyze an image payload yielding rich descriptive text.

        Args:
            image_bytes: The raw byte payload of the image attachment.
            filename: Original filename to parse extension type.

        Returns:
            The described text alt-representation.
        """
        import asyncio
        import os
        import tempfile

        _, ext = os.path.splitext(filename)
        if not ext:
            ext = ".png"

        fd, temp_path = tempfile.mkstemp(suffix=ext, prefix="hermes_vision_")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(image_bytes)

            logger.info(
                f"Analyzing incoming vision payload {len(image_bytes)} bytes resolving natively."
            )

            prompt = "Please describe this image in detail. Be precise."

            # Using asyncio.to_thread because analyzing vision could block
            result = await asyncio.to_thread(
                self._client.analyze_image, temp_path, prompt
            )

            return result.text
        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            raise
        finally:
            try:
                os.remove(temp_path)
            except OSError:
                pass


class DocumentParser:
    """Wrapper for native document text extraction of raw channel payloads."""

    def __init__(self) -> None:
        """Initialize document parsing dependencies."""

    async def extract_text(self, document_bytes: bytes, filename: str) -> str:
        """Extract readable text from document payload bytes.

        Args:
            document_bytes: The raw byte payload of the document.
            filename: Original filename to parse extension type.

        Returns:
            The extracted text strings.
        """
        import asyncio
        import os
        import tempfile

        from codomyrmex.documents import read_pdf

        _, ext = os.path.splitext(filename.lower())

        if ext == ".txt":
            return document_bytes.decode("utf-8", errors="replace")

        if ext == ".pdf":
            fd, temp_path = tempfile.mkstemp(suffix=".pdf", prefix="hermes_doc_")
            try:
                with os.fdopen(fd, "wb") as f:
                    f.write(document_bytes)

                logger.info(
                    f"Extracting PDF text from payload {len(document_bytes)} bytes resolving natively."
                )

                # Use to_thread as PDF parsing can be CPU blocking
                doc = await asyncio.to_thread(read_pdf, temp_path)
                return doc.content
            except Exception as e:
                logger.error(f"Document extraction failed: {e}")
                raise
            finally:
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

        raise ValueError(f"Unsupported document extension: {ext}")
