#!/usr/bin/env python3
"""
Multimodal Image Generation Orchestrator

Config-driven orchestrator for generating images via Google AI (Imagen 3).
Reads all generation parameters from config/multimodal/config.yaml.

Requirements:
    uv sync
    GEMINI_API_KEY environment variable (for live generation)

Usage:
    # Dry run (no API key needed)
    uv run python scripts/multimodal/orchestrate.py

    # Live generation
    GEMINI_API_KEY=<key> uv run python scripts/multimodal/orchestrate.py

    # Override prompt
    GEMINI_API_KEY=<key> uv run python scripts/multimodal/orchestrate.py --prompt "A mountain at sunset"
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

from codomyrmex.multimodal.image_generation import ImageGenerator
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_section,
    print_success,
    print_warning,
    setup_logging,
)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_CONFIG_PATH = _PROJECT_ROOT / "config" / "multimodal" / "config.yaml"


def load_config() -> dict:
    with open(_CONFIG_PATH) as f:
        return yaml.safe_load(f)


def run_image_generation(config: dict, prompt_override: str | None = None) -> bool:
    """Generate images using parameters from config.

    Returns True on success or soft-skip (no API key), False on error.
    """
    gen_cfg = config.get("generation", {}).get("image", {})

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print_warning("GEMINI_API_KEY not set — skipping live generation.")
        print_info("  Export GEMINI_API_KEY=<your-key> to enable generation.")
        print_info(f"  Config: {_CONFIG_PATH.relative_to(_PROJECT_ROOT)}")
        return True

    model = gen_cfg.get("model", "imagen-3.0-generate-002")
    prompt = prompt_override or gen_cfg.get(
        "default_prompt",
        "A photorealistic landscape at golden hour",
    )
    number_of_images = gen_cfg.get("number_of_images", 1)
    aspect_ratio = gen_cfg.get("aspect_ratio", "1:1")
    output_dir = _PROJECT_ROOT / gen_cfg.get("output_dir", "outputs/images")
    save_format = gen_cfg.get("save_format", "png")

    print_info(f"  Model:            {model}")
    print_info(f"  Prompt:           {prompt[:80]}")
    print_info(f"  Images:           {number_of_images}")
    print_info(f"  Aspect ratio:     {aspect_ratio}")
    print_info(f"  Output dir:       {gen_cfg.get('output_dir', 'outputs/images')}")

    try:
        generator = ImageGenerator()
        print_info("  Calling Google AI Imagen 3...")
        results = generator.generate(
            prompt=prompt,
            model=model,
            number_of_images=number_of_images,
            aspect_ratio=aspect_ratio,
        )
    except Exception as e:
        print_error(f"  Generation failed: {e}")
        return False

    print_success(f"  Generated {len(results)} image(s).")

    output_dir.mkdir(parents=True, exist_ok=True)
    saved = 0
    for i, img in enumerate(results):
        image_bytes = img.get("image_bytes") or img.get("image_data")
        if image_bytes:
            out_path = output_dir / f"image_{i + 1}.{save_format}"
            out_path.write_bytes(image_bytes)
            print_success(f"  [{i + 1}] Saved → {out_path.relative_to(_PROJECT_ROOT)}")
            saved += 1
        else:
            print_info(f"  [{i + 1}] Result keys: {list(img.keys())}")

    if saved:
        print_success(f"  {saved} file(s) written to {gen_cfg.get('output_dir', 'outputs/images')}")

    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Multimodal image generation orchestrator"
    )
    parser.add_argument("--prompt", help="Override default prompt from config")
    return parser.parse_args()


def main() -> int:
    setup_logging()
    args = parse_args()

    print_section("Multimodal Image Generation Orchestrator")
    print_info(f"Config: {_CONFIG_PATH.relative_to(_PROJECT_ROOT)}")

    config = load_config()
    ok = run_image_generation(config, prompt_override=args.prompt)

    if ok:
        print_section("Orchestration Complete")
        return 0
    else:
        print_error("Orchestration failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
