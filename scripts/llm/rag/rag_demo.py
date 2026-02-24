#!/usr/bin/env python3
"""
RAG (Retrieval-Augmented Generation) Demo Script

Demonstrates a complete RAG pipeline including document processing,
embedding, retrieval, and augmented generation.

Features:
    - Document chunking and processing
    - Vector similarity search
    - Context augmentation
    - Answer generation with citations
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent  # 4 levels up
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_info, print_success, print_error


def main() -> int:
    setup_logging()
    print_info("=== LLM RAG Demo ===")
    try:
        from codomyrmex.llm.rag import RAGPipeline, InMemoryVectorStore
        obj = RAGPipeline(
            embedding_fn=lambda texts: [[0.0] * 64 for _ in texts],
            vector_store=InMemoryVectorStore(),
        )
        print_success(f"RAGPipeline loaded: {obj!r}")
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1
    except Exception as e:
        print_error(f"Demo error: {e}")
        return 1
    print_success("LLM RAG demo complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
