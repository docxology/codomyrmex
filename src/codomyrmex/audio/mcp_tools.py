"""MCP tools for the audio module."""

import os
from pathlib import Path
from typing import Any, Dict, List

from codomyrmex.model_context_protocol.tool_decorator import mcp_tool
from codomyrmex.audio import Transcriber, WhisperModelSize


@mcp_tool(category="audio")
def audio_get_capabilities() -> dict:
    """Return available audio processing capabilities.

    Reports which speech-to-text and text-to-speech providers are
    installed and ready to use.

    Returns:
        Dictionary with lists of available STT and TTS providers.
    """
    try:
        capabilities: dict = {
            "stt_providers": [],
            "tts_providers": [],
        }

        try:
            import whisper  # noqa: F401
            capabilities["stt_providers"].append("whisper")
        except ImportError:
            pass

        try:
            import pyttsx3  # noqa: F401
            capabilities["tts_providers"].append("pyttsx3")
        except ImportError:
            pass

        try:
            import edge_tts  # noqa: F401
            capabilities["tts_providers"].append("edge-tts")
        except ImportError:
            pass

        return {
            "status": "success",
            "capabilities": capabilities,
            "ready": bool(capabilities["stt_providers"] or capabilities["tts_providers"]),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="audio")
def audio_list_voices(provider: str = "pyttsx3") -> dict:
    """List available text-to-speech voices for a given provider.

    Args:
        provider: TTS provider to query ('pyttsx3' or 'edge-tts')

    Returns:
        Dictionary with a list of available voice names.
    """
    try:
        if provider == "pyttsx3":
            try:
                import pyttsx3
                engine = pyttsx3.init()
                voices = engine.getProperty("voices")
                voice_list = [
                    {"id": v.id, "name": v.name, "languages": v.languages}
                    for v in (voices or [])
                ]
                engine.stop()
                return {"status": "success", "provider": provider, "voices": voice_list}
            except ImportError:
                return {"status": "error", "message": "pyttsx3 not installed. Run: uv sync --extra audio"}

        if provider == "edge-tts":
            try:
                import asyncio

                import edge_tts
                voices_raw = asyncio.run(edge_tts.list_voices())
                voice_list = [{"name": v["ShortName"], "locale": v["Locale"]} for v in voices_raw]
                return {"status": "success", "provider": provider, "voices": voice_list}
            except ImportError:
                return {"status": "error", "message": "edge-tts not installed. Run: uv sync --extra audio"}

        return {"status": "error", "message": f"Unknown provider: {provider!r}. Use 'pyttsx3' or 'edge-tts'"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="audio")
def audio_list_formats() -> Dict[str, List[str]]:
    """List supported audio formats for processing.

    Returns:
        Dictionary with a list of supported audio formats.
    """
    return {
        "status": "success",
        "supported_formats": [
            "wav", "mp3", "flac", "ogg", "m4a", "webm", "mp4", "opus"
        ]
    }


@mcp_tool(category="audio")
def audio_get_info(filepath: str) -> Dict[str, Any]:
    """Get metadata about an audio file.

    Args:
        filepath: Path to the audio file

    Returns:
        Dictionary containing file metadata like size and extension.
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return {"status": "error", "message": f"File not found: {filepath}"}

        if not path.is_file():
            return {"status": "error", "message": f"Path is not a file: {filepath}"}

        stat = path.stat()
        extension = path.suffix.lower().lstrip('.')

        return {
            "status": "success",
            "metadata": {
                "filepath": str(path.absolute()),
                "filename": path.name,
                "extension": extension,
                "size_bytes": stat.st_size,
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="audio")
def audio_transcribe(
    filepath: str,
    language: str | None = None,
    model_size: str = "base"
) -> Dict[str, Any]:
    """Transcribe an audio file to text using available STT provider.

    Args:
        filepath: Path to the audio file
        language: Optional language code (e.g., 'en', 'es'). Auto-detects if None.
        model_size: Whisper model size to use ('tiny', 'base', 'small', 'medium', 'large')

    Returns:
        Dictionary containing transcription text and metadata.
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return {"status": "error", "message": f"File not found: {filepath}"}

        # Convert string to enum
        try:
            size_enum = WhisperModelSize(model_size)
        except ValueError:
            return {
                "status": "error",
                "message": f"Invalid model size: {model_size}. Valid options: " +
                           ", ".join([e.value for e in WhisperModelSize])
            }

        transcriber = Transcriber(model_size=size_enum)
        result = transcriber.transcribe(str(path), language=language)

        return {
            "status": "success",
            "text": result.text,
            "language": result.language,
            "duration": result.duration,
            "segments": [
                {
                    "start": seg.start,
                    "end": seg.end,
                    "text": seg.text
                }
                for seg in result.segments
            ]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
