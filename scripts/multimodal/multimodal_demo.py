#!/usr/bin/env python3
"""
Multimodal Image Generation Demo

Demonstrates the ImageGenerator module using Google AI (Imagen 3).
Loads configuration from config/multimodal/config.yaml.

Requirements:
    uv sync  # google-genai is a core dependency
    GEMINI_API_KEY environment variable

Usage:
    uv run python scripts/multimodal/multimodal_demo.py
    GEMINI_API_KEY=<key> uv run python scripts/multimodal/multimodal_demo.py
"""

import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required: uv add pyyaml")
    sys.exit(1)

# Ensure codomyrmex is importable from the repo root
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
from codomyrmex.multimodal.image_generation import ImageGenerator


_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_CONFIG_PATH = _PROJECT_ROOT / "config" / "multimodal" / "config.yaml"


def load_config() -> dict:
    with open(_CONFIG_PATH) as f:
        return yaml.safe_load(f)


def demo_image_generation(config: dict) -> bool:
    """Run image generation demo — returns True on success, False on failure."""
    gen_cfg = config.get("generation", {}).get("image", {})

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print_error("GEMINI_API_KEY not set — cannot run live API call.")
        print_info("  Set GEMINI_API_KEY to run actual image generation.")
        return False

    model = gen_cfg.get("model", "imagen-4.0-generate-001")
    prompt = gen_cfg.get(
        "default_prompt",
        "A photorealistic blue butterfly on a sunlit dandelion",
    )
    number_of_images = gen_cfg.get("number_of_images", 1)
    aspect_ratio = gen_cfg.get("aspect_ratio", "1:1")
    output_dir = _PROJECT_ROOT / gen_cfg.get("output_dir", "output/images")
    save_format = gen_cfg.get("save_format", "png")

    print_info(f"  Model:            {model}")
    print_info(f"  Prompt:           {prompt[:72]}...")
    print_info(f"  Number of images: {number_of_images}")
    print_info(f"  Aspect ratio:     {aspect_ratio}")

    try:
        generator = ImageGenerator()
        results = generator.generate(
            prompt=prompt,
            model=model,
            number_of_images=number_of_images,
            aspect_ratio=aspect_ratio,
        )
    except Exception as e:
        print_error(f"  Image generation failed: {e}")
        return False

    print_success(f"  Generated {len(results)} image(s).")

    output_dir.mkdir(parents=True, exist_ok=True)
    for i, img in enumerate(results):
        image_bytes = img.get("image_bytes") or img.get("image_data")
        if image_bytes:
            out_path = output_dir / f"demo_image_{i + 1}.{save_format}"
            out_path.write_bytes(image_bytes)
            print_success(f"  Saved: {out_path.relative_to(_PROJECT_ROOT)}")
        else:
            print_info(f"  Image {i + 1} result keys: {list(img.keys())}")

    return True


def main() -> int:
    setup_logging()
    print_section("Multimodal Image Generation Demo")

    config = load_config()
    print_info(f"Config loaded from: {_CONFIG_PATH.relative_to(_PROJECT_ROOT)}")

    ok = demo_image_generation(config)
    if ok:
        print_section("Demo Complete")
        return 0
    else:
        print_error("Demo encountered errors.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
