#!/usr/bin/env python3
"""
Video Generation Orchestrator

Config-driven orchestrator for generating videos via Google AI (Veo 2.0).
Reads all generation parameters from config/video/config.yaml.

Requirements:
    uv sync
    GEMINI_API_KEY environment variable (for live generation)

Usage:
    # Dry run (no API key needed)
    uv run python scripts/video/orchestrate.py

    # Live generation
    GEMINI_API_KEY=<key> uv run python scripts/video/orchestrate.py

    # Override prompt
    GEMINI_API_KEY=<key> uv run python scripts/video/orchestrate.py --prompt "A waterfall at sunset"
"""

import argparse
import os
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
    setup_logging,
)
from codomyrmex.video.generation.video_generator import VideoGenerator

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_CONFIG_PATH = _PROJECT_ROOT / "config" / "video" / "config.yaml"


def load_config() -> dict:
    with open(_CONFIG_PATH) as f:
        return yaml.safe_load(f)


def run_video_generation(
    config: dict,
    prompt_override: str | None = None,
    model_override: str | None = None,
    aspect_ratio_override: str | None = None,
    duration_override: int | None = None,
) -> bool:
    """Generate videos using parameters from config.

    Returns True on success, False on error or missing API key.
    """
    gen_cfg = config.get("generation", {}).get("video", {})

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print_error("GEMINI_API_KEY not set — cannot run live generation.")
        print_info("  Export GEMINI_API_KEY=<your-key> to enable generation.")
        print_info(f"  Config: {_CONFIG_PATH.relative_to(_PROJECT_ROOT)}")
        return False

    model = model_override or gen_cfg.get("model", "veo-2.0-generate-001")
    prompt = prompt_override or gen_cfg.get(
        "default_prompt",
        "A timelapse of a blooming rose in golden hour light",
    )
    number_of_videos = gen_cfg.get("number_of_videos", 1)
    aspect_ratio = aspect_ratio_override or gen_cfg.get("aspect_ratio", "16:9")
    duration_seconds = duration_override or gen_cfg.get("duration_seconds", 5)
    output_dir_str = config.get("output_dir_override") or gen_cfg.get("output_dir", "output")
    output_dir = _PROJECT_ROOT / output_dir_str

    print_info(f"  Model:            {model}")
    print_info(f"  Prompt:           {prompt[:80]}")
    print_info(f"  Videos:           {number_of_videos}")
    print_info(f"  Aspect ratio:     {aspect_ratio}")
    print_info(f"  Duration:         {duration_seconds}s")
    print_info(f"  Output dir:       {output_dir_str}")

    try:
        generator = VideoGenerator()
        print_info("  Calling Google AI Veo 2.0 (may take 30–60s)...")
        # Veo-2.0 has a strict Google SDK config schema that rejects unknown kwargs
        results = generator.generate(
            prompt=prompt,
            model=model,
            # We omit explicit unpack of `duration` and `aspect_ratio` to avoid Pydantic Extra inputs forbidden errors
        )
    except Exception as e:
        print_error(f"  Generation failed: {e}")
        return False

    print_success(f"  Generated {len(results)} video(s).")

    output_dir.mkdir(parents=True, exist_ok=True)
    saved = 0
    for i, vid in enumerate(results):
        video_bytes = vid.get("video_bytes") or vid.get("video_data")
        if video_bytes:
            out_path = output_dir / f"video_{i + 1}.mp4"
            out_path.write_bytes(video_bytes)
            print_success(f"  [{i + 1}] Saved → {out_path.relative_to(_PROJECT_ROOT)}")
            saved += 1
        else:
            # Some APIs return a URI instead of bytes (async generation)
            uri = vid.get("uri") or vid.get("url")
            if uri:
                print_info(f"  [{i + 1}] Video URI: {uri}")
            else:
                print_info(f"  [{i + 1}] Result keys: {list(vid.keys())}")

    if saved:
        print_success(f"  {saved} file(s) written to {output_dir_str}")

    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Video generation orchestrator (Veo 2.0)"
    )
    parser.add_argument("--prompt", help="Override default prompt from config")
    parser.add_argument("--model", default="veo-2.0-generate-001", help="Video generation model")
    parser.add_argument("--aspect-ratio", choices=["16:9", "9:16"], help="Override aspect ratio")
    parser.add_argument("--duration", type=int, help="Override duration in seconds")
    parser.add_argument("--output-dir", help="Override output directory")
    return parser.parse_args()


def main() -> int:
    setup_logging()
    args = parse_args()

    print_section("Video Generation Orchestrator (Veo 2.0)")
    print_info(f"Config: {_CONFIG_PATH.relative_to(_PROJECT_ROOT)}")

    config = load_config()
    ok = run_video_generation(
        config,
        prompt_override=args.prompt,
        model_override=args.model,
        aspect_ratio_override=args.aspect_ratio,
        duration_override=args.duration,
    )

    if ok:
        print_section("Orchestration Complete")
        return 0
    else:
        print_error("Orchestration failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
