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
from codomyrmex.multimodal.image_generation import ImageGenerator


def main() -> int:
    setup_logging()
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
        print_warning("2. GEMINI_API_KEY not set — skipping live generation.")
        print_info("   Export GEMINI_API_KEY=<key> to run actual generation.")
        print_section("Basic Usage Complete (API skipped)")
        return 0

    # ── 3. Generate a single image ─────────────────────────────────────
    print_info("2. Generating a single image (Imagen 3, 1:1)...")
    try:
        results = generator.generate(
            prompt="A photorealistic blue butterfly resting on a dandelion, morning light, macro photography",
            model="imagen-3.0-generate-002",
            number_of_images=1,
            aspect_ratio="1:1",
        )
        print_success(f"   Got {len(results)} result(s). Keys: {list(results[0].keys())}")
    except Exception as e:
        print_error(f"   Single image generation failed: {e}")
        return 1

    # ── 4. Save the image ──────────────────────────────────────────────
    print_info("3. Saving result...")
    output_dir = Path(__file__).resolve().parents[3] / "outputs" / "images"
    output_dir.mkdir(parents=True, exist_ok=True)
    img = results[0]
    image_bytes = img.get("image_bytes") or img.get("image_data")
    if image_bytes:
        out = output_dir / "basic_usage_image.png"
        out.write_bytes(image_bytes)
        print_success(f"   Saved: outputs/images/basic_usage_image.png ({len(image_bytes):,} bytes)")
    else:
        print_info(f"   No image_bytes in result — available keys: {list(img.keys())}")

    # ── 5. Different aspect ratio ──────────────────────────────────────
    print_info("4. Generating a 16:9 landscape image...")
    try:
        wide_results = generator.generate(
            prompt="A cinematic mountain panorama at golden hour, wide format",
            model="imagen-3.0-generate-002",
            number_of_images=1,
            aspect_ratio="16:9",
        )
        print_success(f"   16:9 image generated. Keys: {list(wide_results[0].keys())}")
    except Exception as e:
        print_error(f"   16:9 generation failed: {e}")

    print_section("Basic Usage Complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
