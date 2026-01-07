#!/usr/bin/env python3
"""
Orchestrator script for generating the Codomyrmex website.
"""
import argparse
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.website.generator import WebsiteGenerator

def main():
    parser = argparse.ArgumentParser(description="Generate the Codomyrmex website.")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./output/website",
        help="Directory to write the generated website to."
    )
    
    args = parser.parse_args()
    
    output_path = Path(args.output_dir).resolve()
    
    # Initialize and run generator
    try:
        generator = WebsiteGenerator(output_dir=output_path, root_dir=PROJECT_ROOT)
        generator.generate()
        print(f"\nSuccess! Website generated at: {output_path}/index.html")
    except Exception as e:
        print(f"Error generating website: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
