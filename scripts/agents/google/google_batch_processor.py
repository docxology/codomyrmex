#!/usr/bin/env python3
"""
google_batch_processor.py

Vertex AI Serverless Batch Document Processing.
Process thousands of docs concurrently without hitting rate limits via intelligent semaphores.

Usage:
  ./google_batch_processor.py /path/to/docs --jobs=10 --schema="{\"type\": \"object\"}"
"""

import argparse
import asyncio
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


async def process_document(client, model, file_path, schema, semaphore):
    """Process a single document with rate limit protection."""
    async with semaphore:
        logger.debug("Processing %s...", file_path.name)
        try:
            # Note: The unified SDK's async capabilities might be evolving.
            # We map this to the standard generate_content using asyncio.to_thread if native async is unavailable.
            # Assuming standard API calls for this thin wrapper snippet.
            import asyncio

            def run_sync():
                if file_path.suffix.lower() == ".pdf":
                    mime = "application/pdf"
                else:
                    mime = "text/plain"

                # Real implementation would upload to GCS first for Vertex batch processing.
                # For this thin script, we use inline files for simplicity. (Note: large files need URI)
                with open(file_path, "rb" if mime == "application/pdf" else "r") as f:
                    data = f.read()

                return client.models.generate_content(
                    model=model,
                    contents=[
                        f"Extract data according to this JSON schema: {schema}",
                        types.Part.from_bytes(data=data, mime_type=mime)
                        if isinstance(data, bytes)
                        else data,
                    ],
                    config=types.GenerateContentConfig(
                        temperature=0.0, response_mime_type="application/json"
                    ),
                )

            loop = asyncio.get_running_loop()
            resp = await loop.run_in_executor(None, run_sync)
            return file_path.name, resp.text

        except Exception as e:
            logger.error("Failed processing %s: %s", file_path.name, e)
            return file_path.name, f'{{"error": "{e!s}"}}'


async def async_main(args):
    """Main async execution."""
    client = genai.Client()
    folder = Path(args.input_dir)

    files_to_process = list(folder.glob("*.*"))
    if not files_to_process:
        logger.error("No files found in %s", args.input_dir)
        sys.exit(1)

    logger.info(
        "Found %d files to process. Using %d concurrent workers.",
        len(files_to_process),
        args.jobs,
    )
    semaphore = asyncio.Semaphore(args.jobs)

    tasks = [
        process_document(client, args.model, f, args.schema, semaphore)
        for f in files_to_process
    ]

    results = await asyncio.gather(*tasks)

    # Save results
    output_path = Path(args.output)
    output_dict = {
        fname: (eval(content) if content.strip().startswith("{") else content)
        for fname, content in results
    }

    import json

    with open(output_path, "w") as f:
        json.dump(output_dict, f, indent=2)

    logger.info("Batch processing complete. Results saved to %s", output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Google Batch Processor (Serverless concurrency)"
    )
    parser.add_argument("input_dir", type=str, help="Directory containing documents")
    parser.add_argument("--jobs", type=int, default=5, help="Concurrent jobs limit")
    parser.add_argument(
        "--schema", type=str, required=True, help="JSON Schema string for extraction"
    )
    parser.add_argument(
        "--model", type=str, default="gemini-1.5-pro", help="Model to use"
    )
    parser.add_argument(
        "--output", type=str, default="batch_results.json", help="Output file"
    )
    args = parser.parse_args()

    if not GENAI_AVAILABLE:
        logger.error("google-genai SDK not available.")
        sys.exit(1)

    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
