#!/usr/bin/env python3
"""
Audio Synthesis Orchestrator

Config-driven orchestrator for generating audio via TTS providers.
Reads all parameters from config/audio/config.yaml.

Providers (configured in config):
  - edge-tts:  Microsoft Edge Neural TTS (300+ voices, requires internet)
  - pyttsx3:   Offline TTS using system voices (no internet needed)

Requirements:
    uv sync --extra audio   # for TTS providers
    # No API key needed for pyttsx3; edge-tts uses Microsoft's free endpoint

Usage:
    # Dry run / list providers
    uv run python scripts/audio/orchestrate.py

    # With audio extras installed
    uv sync --extra audio && uv run python scripts/audio/orchestrate.py

    # Override text
    uv run python scripts/audio/orchestrate.py --text "Hello, world!"

    # Force a specific provider
    uv run python scripts/audio/orchestrate.py --provider pyttsx3
"""

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required: uv add pyyaml")
    sys.exit(1)

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_section,
    print_success,
    print_warning,
    setup_logging,
)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_CONFIG_PATH = _PROJECT_ROOT / "config" / "audio" / "config.yaml"


def load_config() -> dict:
    with open(_CONFIG_PATH) as f:
        return yaml.safe_load(f)


def run_audio_synthesis(
    config: dict,
    text_override: str | None = None,
    provider_override: str | None = None,
    voice_override: str | None = None,
    rate_override: float | None = None,
) -> bool:
    """Synthesize audio using parameters from config.

    Tries the configured default_provider first; falls back to fallback_provider.
    Returns True on success, False on error.
    """
    # Late import — audio is an optional extra
    try:
        from codomyrmex.audio import TTS_AVAILABLE, Synthesizer
        from codomyrmex.audio.exceptions import (
            ProviderNotAvailableError,
            SynthesisError,
        )
    except ImportError:
        print_error("Audio module not available.")
        print_info("  Install audio extras: uv sync --extra audio")
        return False  # Soft skip -> strict fail

    if not TTS_AVAILABLE:
        print_error("TTS providers not installed.")
        print_info("  Install: uv sync --extra audio")
        return False

    tts_cfg = config.get("generation", {}).get("tts", {})

    default_provider = provider_override or tts_cfg.get("default_provider", "edge-tts")
    fallback_provider = tts_cfg.get("fallback_provider", "pyttsx3")
    voice = voice_override or tts_cfg.get("default_voice", "en-US-AriaNeural")
    rate = rate_override or tts_cfg.get("rate", 1.0)
    pitch = tts_cfg.get("pitch", 1.0)
    volume = tts_cfg.get("volume", 1.0)
    output_dir = _PROJECT_ROOT / tts_cfg.get("output_dir", "output/audio")
    text = text_override or tts_cfg.get(
        "default_text",
        "Hello! This is a test of the Codomyrmex audio synthesis system.",
    )
    prompts = tts_cfg.get("prompts", [])

    print_info(
        f"  Provider:         {default_provider} (fallback: {fallback_provider})"
    )
    print_info(f"  Voice:            {voice}")
    print_info(f"  Rate/Pitch/Vol:   {rate} / {pitch} / {volume}")
    print_info(f"  Output dir:       {tts_cfg.get('output_dir', 'output/audio')}")
    print_info(f"  Text:             {text[:72]}...")

    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Single synthesis ───────────────────────────────────────────────
    synth = None
    provider_used = default_provider
    for provider in (default_provider, fallback_provider):
        try:
            synth = Synthesizer(provider=provider)
            provider_used = provider
            print_success(f"  Provider '{provider}' initialised.")
            break
        except (ProviderNotAvailableError, ImportError) as e:
            print_warning(f"  Provider '{provider}' unavailable: {e}")

    if synth is None:
        print_error("  No TTS provider available. Install audio extras.")
        return False

    # Single synthesis
    print_info("  Synthesizing single text...")
    try:
        out_path = output_dir / "orchestrate_single.mp3"
        voice_arg = voice if provider_used == "edge-tts" else None
        synth.synthesize_to_file(text, out_path, voice=voice_arg, rate=rate)
        print_success(f"  Saved: {out_path.relative_to(_PROJECT_ROOT)}")
    except SynthesisError as e:
        print_error(f"  Synthesis failed: {e}")
        return False

    # Multi-prompt batch synthesis
    if prompts:
        print_info(f"  Synthesizing from custom prompts ({len(prompts)} texts)...")
        for i, act_prompt in enumerate(prompts):
            try:
                out_path = output_dir / f"audio_{i + 1}.mp3"
                synth.synthesize_to_file(
                    act_prompt, out_path, voice=voice_arg, rate=rate
                )
                print_success(f"  [{i + 1}] Saved: {out_path.name}")
            except SynthesisError as e:
                print_warning(f"  [{i + 1}] Failed: {e}")

    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audio synthesis orchestrator (edge-tts / pyttsx3)"
    )
    parser.add_argument("--text", help="Override default text from config")
    parser.add_argument(
        "--provider",
        choices=["edge-tts", "pyttsx3"],
        help="Override default provider from config",
    )
    parser.add_argument("--voice", help="Override specific voice to use")
    parser.add_argument("--rate", type=float, help="Override speaking rate")
    return parser.parse_args()


def main() -> int:
    setup_logging()
    args = parse_args()

    print_section("Audio Synthesis Orchestrator")
    print_info(f"Config: {_CONFIG_PATH.relative_to(_PROJECT_ROOT)}")

    config = load_config()
    ok = run_audio_synthesis(
        config,
        text_override=args.text,
        provider_override=args.provider,
    )

    if ok:
        print_section("Orchestration Complete")
        return 0
    print_error("Orchestration failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
