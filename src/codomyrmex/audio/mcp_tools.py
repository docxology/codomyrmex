"""MCP tools for the audio module."""

from codomyrmex.model_context_protocol.decorators import mcp_tool


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
            "ready": bool(
                capabilities["stt_providers"] or capabilities["tts_providers"]
            ),
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
