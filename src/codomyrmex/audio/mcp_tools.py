"""MCP tools for the audio module."""

import importlib.util
from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="audio")
def audio_get_capabilities() -> dict[str, Any]:
    """Return available audio processing capabilities.

    Reports which speech-to-text and text-to-speech providers are
    installed and ready to use.

    Returns:
        Dictionary with lists of available STT and TTS providers.

    """
    try:
        capabilities: dict[str, list[str]] = {
            "stt_providers": [],
            "tts_providers": [],
        }

        if importlib.util.find_spec("whisper") is not None:
            capabilities["stt_providers"].append("whisper")

        if importlib.util.find_spec("pyttsx3") is not None:
            capabilities["tts_providers"].append("pyttsx3")

        if importlib.util.find_spec("edge_tts") is not None:
            capabilities["tts_providers"].append("edge-tts")

        return {
            "status": "success",
            "capabilities": capabilities,
            "ready": bool(
                capabilities["stt_providers"] or capabilities["tts_providers"]
            ),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="audio")
def audio_list_voices(provider: str = "pyttsx3") -> dict[str, Any]:
    """list available text-to-speech voices for a given provider.

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
                return {
                    "status": "error",
                    "message": "pyttsx3 not installed. Run: uv sync --extra audio",
                }

        if provider == "edge-tts":
            try:
                import asyncio

                import edge_tts

                voices_raw = asyncio.run(edge_tts.list_voices())
                voice_list = [
                    {"name": v["ShortName"], "locale": v["Locale"]} for v in voices_raw
                ]
                return {"status": "success", "provider": provider, "voices": voice_list}
            except ImportError:
                return {
                    "status": "error",
                    "message": "edge-tts not installed. Run: uv sync --extra audio",
                }

        return {
            "status": "error",
            "message": f"Unknown provider: {provider!r}. Use 'pyttsx3' or 'edge-tts'",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="audio")
def audio_transcribe(
    audio_path: str,
    language: str | None = None,
    model_size: str = "base",
    output_format: str = "text",
    word_timestamps: bool = True,
) -> dict[str, Any]:
    """Transcribe speech from an audio file to text using Whisper.

    Args:
        audio_path: Path to the audio file to transcribe
        language: ISO 639-1 language code (auto-detects if None)
        model_size: Whisper model size
        output_format: Output format ('text', 'srt', 'vtt', 'json')
        word_timestamps: Include word-level timestamps

    Returns:
        Dictionary with transcription results.

    """
    try:
        from codomyrmex.audio.speech_to_text import Transcriber, WhisperModelSize

        model_size_enum = WhisperModelSize(model_size)

        with Transcriber(model_size=model_size_enum) as transcriber:
            result = transcriber.transcribe(
                audio_path,
                language=language,
                word_timestamps=word_timestamps,
            )

        output_file = None
        if output_format == "srt":
            output_file = str(result.save_srt(f"{audio_path}.srt"))
        elif output_format == "vtt":
            output_file = str(result.save_vtt(f"{audio_path}.vtt"))

        result_dict = {
            "text": result.text,
            "language": result.language,
            "language_confidence": result.language_probability,
            "duration": result.duration,
            "segments": [
                {"start": s.start, "end": s.end, "text": s.text}
                for s in result.segments
            ],
        }

        if output_file:
            result_dict["output_file"] = output_file
        elif output_format == "json":
            result_dict = result.to_json()

        return {
            "success": True,
            "result": result_dict,
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "context": {"audio_path": audio_path},
            },
        }


@mcp_tool(category="audio")
def audio_detect_language(audio_path: str) -> dict[str, Any]:
    """Detect the language of speech in an audio file.

    Args:
        audio_path: Path to the audio file

    Returns:
        Dictionary with language detection results.

    """
    try:
        from codomyrmex.audio.speech_to_text import Transcriber

        with Transcriber() as transcriber:
            language, confidence = transcriber.detect_language(audio_path)

        return {
            "success": True,
            "result": {
                "language": language,
                "confidence": confidence,
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "context": {"audio_path": audio_path},
            },
        }


@mcp_tool(category="audio")
def audio_synthesize(
    text: str,
    output_path: str,
    provider: str = "pyttsx3",
    voice: str | None = None,
    rate: float = 1.0,
) -> dict[str, Any]:
    """Generate speech from text using text-to-speech.

    Args:
        text: Text to convert to speech
        output_path: Path to save the audio file
        provider: TTS provider ('pyttsx3' or 'edge-tts')
        voice: Voice ID to use
        rate: Speaking rate

    Returns:
        Dictionary with synthesis results.

    """
    try:
        from codomyrmex.audio.text_to_speech import Synthesizer

        synth = Synthesizer(provider=provider)
        result = synth.synthesize(text, voice=voice, rate=rate)

        saved_path = result.save(output_path)

        return {
            "success": True,
            "result": {
                "output_path": str(saved_path),
                "duration": result.duration,
                "format": result.format.value,
                "voice_used": result.voice_id,
                "file_size_kb": result.size_kb,
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "context": {"text_length": len(text)},
            },
        }


@mcp_tool(category="audio")
def audio_batch_transcribe(
    audio_paths: list[str],
    output_directory: str,
    language: str | None = None,
    model_size: str = "base",
) -> dict[str, Any]:
    """Transcribe multiple audio files in batch.

    Args:
        audio_paths: list of audio file paths
        output_directory: Directory to save transcription files
        language: Language code for all files
        model_size: Whisper model size

    Returns:
        Dictionary with batch transcription results.

    """
    import os

    try:
        from codomyrmex.audio.speech_to_text import Transcriber, WhisperModelSize

        model_size_enum = WhisperModelSize(model_size)

        os.makedirs(output_directory, exist_ok=True)

        results_list = []
        failed = 0

        with Transcriber(model_size=model_size_enum) as transcriber:
            for path in audio_paths:
                try:
                    result = transcriber.transcribe(path, language=language)
                    output_file = os.path.join(
                        output_directory, f"{os.path.basename(path)}.txt"
                    )
                    with open(output_file, "w") as f:
                        f.write(result.text)

                    results_list.append(
                        {
                            "input": path,
                            "output": output_file,
                            "duration": result.duration,
                            "language": result.language,
                        }
                    )
                except Exception as _exc:
                    failed += 1

        return {
            "success": True,
            "result": {
                "processed": len(results_list),
                "failed": failed,
                "results": results_list,
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "context": {"batch_size": len(audio_paths)},
            },
        }
