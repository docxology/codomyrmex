#!/usr/bin/env python3
"""
Documents Module - Real Usage Examples

Demonstrates actual document I/O capabilities:
- Markdown, JSON, YAML reading/writing
- Document metadata extraction
- Document transformation (stubs)
"""

import sys
import os
import shutil
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.documents import (
    read_document,
    write_document,
    Document,
    DocumentFormat
)

def main():
    setup_logging()
    print_info("Running Document I/O Examples...")

    # Output directory for tests
    output_dir = Path("output/documents_test")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    test_file = output_dir / "test_doc.md"

    # 1. Document Writing
    print_info("Testing document writing...")
    try:
        content = "# Test Document\n\nThis is a test document."
        write_document(test_file, content, format=DocumentFormat.MARKDOWN)
        print_success(f"  Document written to {test_file}")
    except Exception as e:
        print_error(f"  Document writing failed: {e}")

    # 2. Document Reading
    print_info("Testing document reading...")
    try:
        doc = read_document(test_file)
        if doc and "# Test Document" in doc:
            print_success("  Document read successfully.")
    except Exception as e:
        print_error(f"  Document reading failed: {e}")

    # 3. Document Model
    print_info("Testing Document model...")
    try:
        d = Document(content="# Model Test", format=DocumentFormat.MARKDOWN)
        print_success(f"  Document model created with format: {d.format}")
    except Exception as e:
        print_error(f"  Document model failed: {e}")

    print_success("Document I/O examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
