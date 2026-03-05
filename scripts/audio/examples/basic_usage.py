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

import argparse
import sys
from pathlib import Path

try:
    import codomyrmex
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


def parse_args():
    parser = argparse.ArgumentParser(description="Audio Basic Usage Example")
    parser.add_argument(
        "--text", default="Hello! This is Codomyrmex.", help="Input for generation"
    )
    parser.add_argument(
        "--provider",
        choices=["edge-tts", "pyttsx3", "auto"],
        default="auto",
        help="TTS Provider to use",
    )
    parser.add_argument(
        "--voice",
        help="Specific voice to use (e.g., en-US-AriaNeural or a system voice ID)",
    )
    parser.add_argument(
        "--rate", type=float, default=1.0, help="Speaking rate (1.0 is normal)"
    )
    parser.add_argument("--output-dir", default="output/audio", help="Output directory")
    return parser.parse_args()


def main() -> int:
    setup_logging()
    args = parse_args()
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
        print_error("Audio module not importable.")
        print_info("  Install: uv sync --extra audio")
        return 1

    if not TTS_AVAILABLE:
        print_error("No TTS providers installed.")
        print_info("  Install: uv sync --extra audio")
        return 1

    print_info(f"  edge-tts available:  {EDGE_TTS_AVAILABLE}")
    print_info(f"  pyttsx3 available:   {PYTTSX3_AVAILABLE}")

    output_dir = Path(__file__).resolve().parents[3] / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Decide provider based on args ────────────────────────────
    use_edge = args.provider in ("edge-tts", "auto") and EDGE_TTS_AVAILABLE
    use_offline = args.provider in ("pyttsx3", "auto") and PYTTSX3_AVAILABLE

    if (
        args.provider != "auto"
        and args.provider == "edge-tts"
        and not EDGE_TTS_AVAILABLE
    ):
        print_error(
            "edge-tts requested but not available. Install: uv sync --extra audio"
        )
        return 1
    if args.provider != "auto" and args.provider == "pyttsx3" and not PYTTSX3_AVAILABLE:
        print_error(
            "pyttsx3 requested but not available. Install: uv sync --extra audio"
        )
        return 1

    success_count = 0

    # ── 1. edge-tts (neural, high-quality) ────────────────────────────
    if use_edge:
        print_info("1. edge-tts — Neural TTS (Microsoft Edge voices)...")
        try:
            synth = Synthesizer(provider="edge-tts")
            print_success("   Synthesizer ready with edge-tts.")

            # Synthesize to file
            out = output_dir / "basic_usage_edge_tts.mp3"
            synth.synthesize_to_file(
                args.text,
                out,
                voice=args.voice or "en-US-AriaNeural",
                rate=args.rate,
            )
            print_success(f"   Saved: {args.output_dir}/basic_usage_edge_tts.mp3")
            success_count += 1

            # Batch synthesis
            batch_texts = [
                "The first sentence in a batch.",
                "The second sentence with different content.",
            ]
            results = synth.synthesize_batch(
                batch_texts, voice=args.voice or "en-US-GuyNeural", rate=args.rate
            )
            print_success(f"   Batch: {len(results)} results synthesized.")

        except ProviderNotAvailableError as e:
            print_error(f"   edge-tts unavailable: {e}")
        except SynthesisError as e:
            print_error(f"   Synthesis failed: {e}")
    elif args.provider == "auto":
        print_warning("1. edge-tts not installed (skip).")

    # ── 2. pyttsx3 (offline, system voices) ───────────────────────────
    if use_offline:
        print_info("2. pyttsx3 — Offline TTS (system voices)...")
        try:
            synth_offline = Synthesizer(provider="pyttsx3")
            print_success("   Synthesizer ready with pyttsx3.")

            out = output_dir / "basic_usage_pyttsx3.wav"
            synth_offline.synthesize_to_file(
                args.text,
                out,
                voice=args.voice,
                rate=args.rate,
            )
            print_success(f"   Saved: {args.output_dir}/basic_usage_pyttsx3.wav")
            success_count += 1

        except ProviderNotAvailableError as e:
            print_error(f"   pyttsx3 unavailable: {e}")
        except SynthesisError as e:
            print_error(f"   Synthesis failed: {e}")
    elif args.provider == "auto":
        print_warning("2. pyttsx3 not installed (skip).")

    # ── 3. In-memory synthesis ─────────────────────────────────────────
    if success_count > 0:
        print_info("3. In-memory synthesis (no file save)...")
        provider = "edge-tts" if use_edge else "pyttsx3"
        try:
            synth_mem = Synthesizer(provider=provider)
            result = synth_mem.synthesize(
                "This is an in-memory synthesis — result.audio_data holds the bytes.",
                voice=args.voice
                or ("en-US-AriaNeural" if provider == "edge-tts" else None),
                rate=args.rate,
            )
            print_success(f"   SynthesisResult: {type(result).__name__}")
            if hasattr(result, "audio_data") and result.audio_data:
                print_success(f"   audio_data: {len(result.audio_data):,} bytes")
        except Exception as e:
            print_error(f"   In-memory synthesis failed: {e}")
    else:
        print_error(
            "3. No provider available for in-memory test, or previous synthesis failed."
        )
        return 1

    print_section("Basic Usage Complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
