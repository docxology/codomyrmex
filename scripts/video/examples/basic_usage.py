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

import argparse
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
    setup_logging,
)
from codomyrmex.video.generation.video_generator import VideoGenerator


def parse_args():
    parser = argparse.ArgumentParser(description="Video Basic Usage Example")
    parser.add_argument(
        "--prompt",
        default="A timelapse of clouds moving over a mountain range, cinematic, golden hour",
        help="Input for generation",
    )
    parser.add_argument(
        "--model", default="veo-2.0-generate-001", help="Video generation model"
    )
    parser.add_argument(
        "--aspect-ratio",
        default="16:9",
        choices=["16:9", "9:16"],
        help="Aspect ratio for the video",
    )
    parser.add_argument("--duration", type=int, default=5, help="Duration in seconds")
    parser.add_argument(
        "--output-dir", default="output", help="Output directory relative to repo root"
    )
    return parser.parse_args()


def main() -> int:
    setup_logging()
    args = parse_args()
    print_section("VideoGenerator — Basic Usage (Veo 2.0)")

    # ── 1. Construction ────────────────────────────────────────────────
    print_info("1. Constructing VideoGenerator (no API call yet)...")
    # Passing no client auto-creates a GeminiClient using GEMINI_API_KEY.
    generator = VideoGenerator()
    print_success(f"   VideoGenerator ready. Client: {type(generator.client).__name__}")

    # ── 2. API key check ───────────────────────────────────────────────
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print_error("2. GEMINI_API_KEY not set — cannot run live generation.")
        print_info("   Export GEMINI_API_KEY=<key> to run actual generation.")
        return 1

    # ── 3. Generate a short video ──────────────────────────────────────
    print_info(
        f"2. Generating a {args.duration}-second {args.aspect_ratio} video ({args.model})..."
    )
    print_info("   Note: Veo 2.0 generation typically takes 30–120 seconds.")
    try:
        # Veo-2.0 has strict config schema. Avoid sending unsupported arguments like `duration`.
        results = generator.generate(
            prompt=args.prompt,
            model=args.model,
        )
        if not results:
            print_error(
                "   No video results returned (possibly filtered or generation failed server-side)."
            )
            return 1
        print_success(
            f"   Got {len(results)} result(s). Keys: {list(results[0].keys())}"
        )
    except Exception as e:
        print_error(f"   Video generation failed: {e}")
        return 1

    # ── 4. Save the video ──────────────────────────────────────────────
    print_info("3. Saving result...")
    output_dir = Path(__file__).resolve().parents[3] / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    vid = results[0]
    video_bytes = vid.get("video_bytes") or vid.get("video_data")
    if video_bytes:
        out = output_dir / "basic_usage_video.mp4"
        out.write_bytes(video_bytes)
        print_success(
            f"   Saved: {args.output_dir}/basic_usage_video.mp4 ({len(video_bytes):,} bytes)"
        )
    else:
        uri = vid.get("uri") or vid.get("url")
        if uri:
            print_info(f"   Video available at URI: {uri}")
        else:
            print_info(f"   No bytes in result — available keys: {list(vid.keys())}")

    # ── 5. Alternative Aspect Ratio video (if default was used) ───────
    alt_ratio = "9:16" if args.aspect_ratio == "16:9" else "16:9"
    print_info(f"4. Generating a {alt_ratio} video...")
    try:
        vertical_results = generator.generate(
            prompt=args.prompt + " (alternative)",
            model=args.model,
            number_of_videos=1,
            aspect_ratio=alt_ratio,
            duration_seconds=args.duration,
        )
        print_success(
            f"   {alt_ratio} video generated. Keys: {list(vertical_results[0].keys())}"
        )
    except Exception as e:
        print_error(f"   Alternative video generation failed: {e}")
        return 1

    print_section("Basic Usage Complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
