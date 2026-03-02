#!/usr/bin/env python3
"""Thin orchestrator script for the dark module.

Demonstrates PDF dark mode processing using different presets and
custom filter configurations.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

# Ensure codomyrmex is in path if running from source
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    import fitz
    from codomyrmex.dark.pdf import DarkPDF, apply_dark_mode
except ImportError as e:
    print(f"Error: Required dependencies not found. {e}")
    print("Please install with: uv sync --extra dark")
    sys.exit(1)


def create_sample_pdf(path: Path) -> None:
    """Create a sample PDF for demonstration."""
    doc = fitz.open()
    page = doc.new_page(width=400, height=400)

    # Add some text and shapes
    page.draw_rect(fitz.Rect(0, 0, 400, 400), color=(1, 1, 1), fill=(1, 1, 1))
    page.insert_text((50, 50), "Codomyrmex Dark Mode Demo", fontsize=20, color=(0, 0, 0))
    page.insert_text(
        (50, 100), "This PDF will be transformed to dark mode.", fontsize=12, color=(0.2, 0.2, 0.2)
    )

    page.draw_circle((200, 250), 50, color=(0.8, 0, 0), fill=(0.8, 0, 0))
    page.draw_rect(fitz.Rect(50, 200, 150, 300), color=(0, 0, 0.8), fill=(0, 0, 0.8))

    doc.save(str(path))
    doc.close()


def main() -> None:
    """Run the orchestrator demo."""
    parser = argparse.ArgumentParser(description="Codomyrmex Dark Mode Orchestrator")
    parser.add_argument("--input", help="Input PDF path (auto-generated if missing)")
    parser.add_argument("--output-dir", default="demo_output", help="Output directory")

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        if args.input:
            input_path = Path(args.input)
        else:
            input_path = Path(tmpdir) / "demo_input.pdf"
            create_sample_pdf(input_path)
            print(f"Generated sample PDF at: {input_path}")

        print("\n--- Starting Dark Mode Transformations ---")

        # 1. Simple one-call API
        out1 = output_dir / "1_simple_dark.pdf"
        apply_dark_mode(input_path, out1)
        print(f"Applied standard dark mode: {out1}")

        # 2. Preset: Sepia
        out2 = output_dir / "2_sepia_preset.pdf"
        DarkPDF(input_path, preset="sepia").save(out2)
        print(f"Applied sepia preset: {out2}")

        # 3. Fluent API with custom adjustments
        out3 = output_dir / "3_custom_fluent.pdf"
        (
            DarkPDF(input_path)
            .set_inversion(0.95)
            .set_brightness(0.8)
            .set_contrast(1.2)
            .set_sepia(0.2)
            .save(out3)
        )
        print(f"Applied custom fluent configuration: {out3}")

        # 4. Batch processing
        batch_inputs = [input_path]
        batch_outputs = DarkPDF.batch(
            batch_inputs,
            output_dir=output_dir / "batch",
            preset="high_contrast"
        )
        print(f"Batch processed {len(batch_outputs)} files to: {output_dir / 'batch'}")

        print("\n--- All transformations complete! ---")
        print(f"View results in: {output_dir.absolute()}")


if __name__ == "__main__":
    main()
