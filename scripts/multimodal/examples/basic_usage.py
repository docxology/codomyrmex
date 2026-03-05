#!/usr/bin/env python3
"""
ImageGenerator — Basic Usage Example

Shows the minimal pattern for generating images with Google AI (Imagen 3)
using the codomyrmex multimodal module.

Requirements:
    uv sync
    GEMINI_API_KEY environment variable (for live API calls)

Usage:
    uv run python scripts/multimodal/examples/basic_usage.py
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

from codomyrmex.multimodal.image_generation import ImageGenerator
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_section,
    print_success,
    setup_logging,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Multimodal Basic Usage Example")
    parser.add_argument(
        "--prompt",
        default="A photorealistic blue butterfly resting on a dandelion, morning light",
        help="Input for generation",
    )
    parser.add_argument(
        "--model", default="imagen-4.0-generate-001", help="Image generation model"
    )
    parser.add_argument(
        "--aspect-ratio",
        default="1:1",
        choices=["1:1", "16:9", "9:16", "4:3", "3:4"],
        help="Aspect ratio for the image",
    )
    parser.add_argument(
        "--images", type=int, default=1, help="Number of images to generate"
    )
    parser.add_argument(
        "--output-dir",
        default="output/images",
        help="Output directory relative to repo root",
    )
    return parser.parse_args()


def main() -> int:
    setup_logging()
    args = parse_args()
    print_section("ImageGenerator — Basic Usage")

    # ── 1. Construction ────────────────────────────────────────────────
    print_info("1. Constructing ImageGenerator (no API call yet)...")
    # Passing no client auto-creates a GeminiClient using GEMINI_API_KEY env var.
    # You can inject a custom GeminiClient for testing or batching.
    generator = ImageGenerator()
    print_success(f"   ImageGenerator ready. Client: {type(generator.client).__name__}")

    # ── 2. API key check ───────────────────────────────────────────────
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print_error("2. GEMINI_API_KEY not set — cannot run live generation.")
        print_info("   Export GEMINI_API_KEY=<key> to run actual generation.")
        return 1

    # ── 3. Generate a single image ─────────────────────────────────────
    print_info(
        f"2. Generating {args.images} image(s) ({args.model}, {args.aspect_ratio})..."
    )
    try:
        results = generator.generate(
            prompt=args.prompt,
            model=args.model,
            number_of_images=args.images,
            aspect_ratio=args.aspect_ratio,
        )
        print_success(
            f"   Got {len(results)} result(s). Keys: {list(results[0].keys())}"
        )
    except Exception as e:
        print_error(f"   Image generation failed: {e}")
        return 1

    # ── 4. Save the image ──────────────────────────────────────────────
    print_info("3. Saving result...")
    output_dir = Path(__file__).resolve().parents[3] / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    img = results[0]
    image_bytes = img.get("image_bytes") or img.get("image_data")
    if image_bytes:
        out = output_dir / "basic_usage_image.png"
        out.write_bytes(image_bytes)
        print_success(
            f"   Saved: {args.output_dir}/basic_usage_image.png ({len(image_bytes):,} bytes)"
        )
    else:
        print_info(f"   No image_bytes in result — available keys: {list(img.keys())}")

    # ── 5. Different aspect ratio ──────────────────────────────────────
    alt_ratio = "16:9" if args.aspect_ratio == "1:1" else "1:1"
    print_info(f"4. Generating a {alt_ratio} landscape image...")
    try:
        wide_results = generator.generate(
            prompt=args.prompt + " (alternative)",
            model=args.model,
            number_of_images=1,
            aspect_ratio=alt_ratio,
        )
        print_success(
            f"   {alt_ratio} image generated. Keys: {list(wide_results[0].keys())}"
        )
    except Exception as e:
        print_error(f"   {alt_ratio} generation failed: {e}")
        return 1

    print_section("Basic Usage Complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
