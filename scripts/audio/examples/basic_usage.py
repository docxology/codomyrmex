#!/usr/bin/env python3
"""
Synthesizer — Basic Usage Example

Shows the minimal patterns for text-to-speech synthesis using both
edge-tts (neural, internet) and pyttsx3 (offline, system voices).

Requirements:
    uv sync --extra audio

Usage:
    uv run python scripts/audio/examples/basic_usage.py
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_section,
    print_success,
    print_warning,
    setup_logging,
)


def main() -> int:
    setup_logging()
    print_section("Synthesizer — Basic Usage (TTS)")

    # ── 0. Import guard ────────────────────────────────────────────────
    try:
        from codomyrmex.audio import (
            EDGE_TTS_AVAILABLE,
            PYTTSX3_AVAILABLE,
            TTS_AVAILABLE,
            Synthesizer,
        )
        from codomyrmex.audio.exceptions import (
            ProviderNotAvailableError,
            SynthesisError,
        )
    except ImportError:
        print_warning("Audio module not importable.")
        print_info("  Install: uv sync --extra audio")
        return 0

    if not TTS_AVAILABLE:
        print_warning("No TTS providers installed.")
        print_info("  Install: uv sync --extra audio")
        return 0

    print_info(f"  edge-tts available:  {EDGE_TTS_AVAILABLE}")
    print_info(f"  pyttsx3 available:   {PYTTSX3_AVAILABLE}")

    output_dir = Path(__file__).resolve().parents[3] / "outputs" / "audio"
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. edge-tts (neural, high-quality) ────────────────────────────
    if EDGE_TTS_AVAILABLE:
        print_info("1. edge-tts — Neural TTS (Microsoft Edge voices)...")
        try:
            synth = Synthesizer(provider="edge-tts")
            print_success("   Synthesizer ready with edge-tts.")

            # List available English voices
            voices = synth.list_voices(language="en-US")
            print_info(f"   en-US voices available: {len(voices)}")
            if voices:
                print_info(f"   Sample voices: {[v.id for v in voices[:3]]}")

            # Synthesize to file
            out = output_dir / "basic_usage_edge_tts.mp3"
            synth.synthesize_to_file(
                "Hello! This is the Codomyrmex audio module using Microsoft Edge neural TTS.",
                out,
                voice="en-US-AriaNeural",
                rate=1.0,
            )
            print_success("   Saved: outputs/audio/basic_usage_edge_tts.mp3")

            # Batch synthesis
            batch_texts = [
                "The first sentence in a batch.",
                "The second sentence with different content.",
            ]
            results = synth.synthesize_batch(batch_texts, voice="en-US-GuyNeural")
            print_success(f"   Batch: {len(results)} results synthesized.")

        except ProviderNotAvailableError as e:
            print_warning(f"   edge-tts unavailable: {e}")
        except SynthesisError as e:
            print_error(f"   Synthesis failed: {e}")
    else:
        print_warning("1. edge-tts not installed (skip). Install: uv sync --extra audio")

    # ── 2. pyttsx3 (offline, system voices) ───────────────────────────
    if PYTTSX3_AVAILABLE:
        print_info("2. pyttsx3 — Offline TTS (system voices)...")
        try:
            synth_offline = Synthesizer(provider="pyttsx3")
            print_success("   Synthesizer ready with pyttsx3.")

            voices = synth_offline.list_voices()
            print_info(f"   System voices available: {len(voices)}")

            out = output_dir / "basic_usage_pyttsx3.wav"
            synth_offline.synthesize_to_file(
                "Hello! This is offline pyttsx3 TTS synthesis.",
                out,
                rate=1.0,
            )
            print_success("   Saved: outputs/audio/basic_usage_pyttsx3.wav")

        except ProviderNotAvailableError as e:
            print_warning(f"   pyttsx3 unavailable: {e}")
        except SynthesisError as e:
            print_error(f"   Synthesis failed: {e}")
    else:
        print_warning("2. pyttsx3 not installed (skip). Install: uv sync --extra audio")

    # ── 3. In-memory synthesis ─────────────────────────────────────────
    print_info("3. In-memory synthesis (no file save)...")
    provider = "edge-tts" if EDGE_TTS_AVAILABLE else ("pyttsx3" if PYTTSX3_AVAILABLE else None)
    if provider:
        try:
            synth_mem = Synthesizer(provider=provider)
            result = synth_mem.synthesize(
                "This is an in-memory synthesis — result.audio_data holds the bytes.",
                voice="en-US-AriaNeural" if provider == "edge-tts" else None,
            )
            # SynthesisResult has .audio_data (bytes) and .save(path) method
            print_success(f"   SynthesisResult: {type(result).__name__}")
            if hasattr(result, "audio_data") and result.audio_data:
                print_success(f"   audio_data: {len(result.audio_data):,} bytes")
        except Exception as e:
            print_error(f"   In-memory synthesis failed: {e}")
    else:
        print_warning("3. No provider available for in-memory test.")

    print_section("Basic Usage Complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
