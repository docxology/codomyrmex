#!/usr/bin/env python3
"""
google_vision_analyzer.py

Multimodal Document+Image Analysis Pipeline.
Analyzes mixed-media folders (PDFs/images) for extraction, OCR, diagramming, and reasoning.

Usage:
  ./google_vision_analyzer.py /path/to/media/folder --tasks=extract,ocr --output=results.json
"""

import argparse
import json
import os
import sys
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

try:
    from google import genai
    from google.genai import types

    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def main():
    parser = argparse.ArgumentParser(
        description="Google Vision Analyzer (Multimodal Pipeline)"
    )
    parser.add_argument(
        "input_dir", type=str, help="Path to folder containing PDFs/Images"
    )
    parser.add_argument(
        "--model", type=str, default="gemini-2.5-pro", help="Model to use"
    )
    parser.add_argument(
        "--tasks",
        type=str,
        default="extract",
        help="Comma-separated list of tasks (e.g. ocr,diagram)",
    )
    parser.add_argument(
        "--output", type=str, default="vision_results.json", help="Output JSON path"
    )
    args = parser.parse_args()

    if not GENAI_AVAILABLE:
        logger.error("google-genai SDK not available.")
        sys.exit(1)

    folder = Path(args.input_dir)
    if not folder.exists() or not folder.is_dir():
        logger.error("Input directory %s does not exist.", args.input_dir)
        sys.exit(1)

    # Initialize client (will pick up Vertex AI auth if set in environment)
    client = genai.Client()

    contents = []
    processed_files = []

    for file in folder.iterdir():
        if file.suffix.lower() in {".png", ".jpg", ".jpeg", ".pdf"}:
            logger.info("Uploading %s...", file.name)
            try:
                # Note: In production, upload to GCS first if using Vertex, or use files.upload for API Studio
                file_uri = client.files.upload(file=str(file))
                contents.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(
                                f"Analyze {file.name}. Tasks: {args.tasks}"
                            ),
                            types.Part.from_uri(
                                file_uri=file_uri.uri,
                                mime_type="application/pdf"
                                if file.suffix.lower() == ".pdf"
                                else "image/jpeg",
                            ),
                        ],
                    )
                )
                processed_files.append(file.name)
            except Exception as e:
                logger.error("Failed to upload/prepare %s: %s", file.name, e)

    if not contents:
        logger.warning("No valid media found in %s", args.input_dir)
        sys.exit(0)

    logger.info("Starting batch multimodal analysis...")
    try:
        # Note: Depending on the backend (Vertex vs Studio), batch syntax varies slightly.
        # This uses the standard unified SDK approach.
        responses = client.models.generate_content(
            model=args.model,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.1, response_mime_type="application/json"
            ),
        )

        # Parse the structured response
        try:
            results = json.loads(responses.text)
        except json.JSONDecodeError:
            results = {"raw_text": responses.text}

        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)

        logger.info("Successfully wrote results to %s", args.output)

    except Exception as e:
        logger.error("Batch inference failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
