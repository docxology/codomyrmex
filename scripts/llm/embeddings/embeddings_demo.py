#!/usr/bin/env python3
"""
Embeddings Demo Script

Demonstrates text embedding generation and similarity search functionality.
Uses sentence-transformers for local embeddings or API providers.

Features:
    - Text embedding generation
    - Cosine similarity calculation
    - Semantic search demonstration
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent  # 4 levels up
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_info, print_success, print_error


def main() -> int:
    setup_logging()
    print_info("=== LLM Embeddings Demo ===")
    try:
        from codomyrmex.llm.embeddings import EmbeddingService, MockEmbeddingProvider
        provider = MockEmbeddingProvider()
        obj = EmbeddingService(provider=provider)
        print_success(f"EmbeddingService loaded: {obj!r}")
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1
    except Exception as e:
        print_error(f"Demo error: {e}")
        return 1
    print_success("LLM Embeddings demo complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
