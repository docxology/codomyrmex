#!/usr/bin/env python3
"""
VideoGenerator — Basic Usage Example

Shows the minimal pattern for generating videos with Google AI (Veo 2.0)
using the codomyrmex video module.

Requirements:
    uv sync
    GEMINI_API_KEY environment variable (for live API calls)

Usage:
    uv run python scripts/video/examples/basic_usage.py
"""

import os
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
from codomyrmex.video.generation.video_generator import VideoGenerator


def main() -> int:
    setup_logging()
    print_section("VideoGenerator — Basic Usage (Veo 2.0)")

    # ── 1. Construction ────────────────────────────────────────────────
    print_info("1. Constructing VideoGenerator (no API call yet)...")
    # Passing no client auto-creates a GeminiClient using GEMINI_API_KEY.
    generator = VideoGenerator()
    print_success(f"   VideoGenerator ready. Client: {type(generator.client).__name__}")

    # ── 2. API key check ───────────────────────────────────────────────
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print_warning("2. GEMINI_API_KEY not set — skipping live generation.")
        print_info("   Export GEMINI_API_KEY=<key> to run actual generation.")
        print_section("Basic Usage Complete (API skipped)")
        return 0

    # ── 3. Generate a short video ──────────────────────────────────────
    print_info("2. Generating a 5-second 16:9 video (Veo 2.0)...")
    print_info("   Note: Veo 2.0 generation typically takes 30–120 seconds.")
    try:
        results = generator.generate(
            prompt="A timelapse of clouds moving over a mountain range, cinematic, golden hour",
            model="veo-2.0-generate-001",
            number_of_videos=1,
            aspect_ratio="16:9",
            duration_seconds=5,
        )
        print_success(
            f"   Got {len(results)} result(s). Keys: {list(results[0].keys())}"
        )
    except Exception as e:
        print_error(f"   Video generation failed: {e}")
        return 1

    # ── 4. Save the video ──────────────────────────────────────────────
    print_info("3. Saving result...")
    output_dir = Path(__file__).resolve().parents[3] / "outputs" / "videos"
    output_dir.mkdir(parents=True, exist_ok=True)
    vid = results[0]
    video_bytes = vid.get("video_bytes") or vid.get("video_data")
    if video_bytes:
        out = output_dir / "basic_usage_video.mp4"
        out.write_bytes(video_bytes)
        print_success(
            f"   Saved: outputs/videos/basic_usage_video.mp4 ({len(video_bytes):,} bytes)"
        )
    else:
        uri = vid.get("uri") or vid.get("url")
        if uri:
            print_info(f"   Video available at URI: {uri}")
        else:
            print_info(f"   No bytes in result — available keys: {list(vid.keys())}")

    # ── 5. Vertical (9:16) video for mobile ───────────────────────────
    print_info("4. Generating a 9:16 vertical video...")
    try:
        vertical_results = generator.generate(
            prompt="A vertical waterfall flowing through a lush forest, slow motion",
            model="veo-2.0-generate-001",
            number_of_videos=1,
            aspect_ratio="9:16",
            duration_seconds=5,
        )
        print_success(
            f"   9:16 video generated. Keys: {list(vertical_results[0].keys())}"
        )
    except Exception as e:
        print_error(f"   Vertical video generation failed: {e}")

    print_section("Basic Usage Complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
