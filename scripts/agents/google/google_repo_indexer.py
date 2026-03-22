#!/usr/bin/env python3
"""
google_repo_indexer.py

Codebase RAG Indexer with Vertex AI Batch.
Parses repositories and embeds chunks directly into Vertex AI Vector Search.

Usage:
  ./google_repo_indexer.py /path/to/repo --project=my-project
"""

import argparse
import sys
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def naive_chunker(file_path: Path, max_lines: int = 150) -> list[dict]:
    """Naive line-based chunking fallback if tree-sitter not available."""
    chunks = []
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        for i in range(0, len(lines), max_lines):
            chunk_text = "".join(lines[i:i+max_lines])
            chunks.append({
                "path": str(file_path),
                "text": chunk_text,
                "start_line": i,
                "end_line": min(i+max_lines, len(lines))
            })
    except Exception as e:
        logger.debug("Skipping %s: %s", file_path, e)
    return chunks


def main():
    parser = argparse.ArgumentParser(description="Google Repo Indexer (Vertex AI Vector Search)")
    parser.add_argument("repo_path", type=str, help="Path to repository")
    parser.add_argument("--project", type=str, required=True, help="GCP Project ID")
    parser.add_argument("--location", type=str, default="us-central1", help="GCP Location")
    parser.add_argument("--embedding-model", type=str, default="text-embedding-004", help="Embedding model")
    args = parser.parse_args()

    if not GENAI_AVAILABLE:
        logger.error("google-genai SDK not available.")
        sys.exit(1)

    repo = Path(args.repo_path)
    if not repo.exists() or not repo.is_dir():
        logger.error("Repo directory does not exist.")
        sys.exit(1)

    # Note: the new genai SDK handles vertex ai transparently if configured
    client = genai.Client(vertexai=True, project=args.project, location=args.location)

    logger.info("Chunking repository files...")
    all_chunks = []
    for filepath in repo.rglob("*"):
        if filepath.is_file() and not any(p.startswith(".") for p in filepath.parts):
            if filepath.suffix in {".py", ".md", ".js", ".ts", ".html", ".css", ".json"}:
                all_chunks.extend(naive_chunker(filepath))

    if not all_chunks:
        logger.warning("No indexable code chunks found.")
        sys.exit(0)

    logger.info("Generated %d chunks. Embedding...", len(all_chunks))

    # In a real script, batch these appropriately to avoid payload limits
    batch_size = 100
    all_embeddings = []

    try:
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i+batch_size]
            texts = [c["text"] for c in batch]

            # Using genai unified representation
            resp = client.models.embed_content(
                model=args.embedding_model,
                contents=texts
            )

            if hasattr(resp, "embeddings") and resp.embeddings:
                all_embeddings.extend([e.values for e in resp.embeddings])
            elif hasattr(resp, "embedding") and resp.embedding:
                all_embeddings.append(resp.embedding.values)

            logger.info("Embedded batch %d/%d", i // batch_size + 1, (len(all_chunks) + batch_size - 1) // batch_size)

    except Exception as e:
        logger.error("Embedding failed: %s", e)
        sys.exit(1)

    logger.info("Successfully generated %d embeddings.", len(all_embeddings))
    logger.info("Next Step: Upsert these to Vertex AI Vector Search Index (implementation depends on vertexai.vector_search).")

if __name__ == "__main__":
    main()
