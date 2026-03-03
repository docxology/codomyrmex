#!/usr/bin/env python3
"""
Documents Module - Basic Usage Examples

Demonstrates core document capabilities:
- Markdown, JSON, YAML, HTML, CSV reading/writing
- Document metadata extraction
- Document transformation and search
"""

import shutil
import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.documents import (
    Document,
    DocumentFormat,
    convert_document,
    create_index,
    index_document,
    merge_documents,
    read_document,
    search_documents,
    split_document,
    write_document,
)
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def main():
    setup_logging()
    print_info("Running Document I/O Examples...")

    # Output directory for tests
    output_dir = Path("output/documents_basic")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Document Creation and Writing
    print_info("Testing document creation and writing...")
    try:
        md_content = "# Hello Codomyrmex\n\nThis is a sample document."
        doc = Document(content=md_content, format=DocumentFormat.MARKDOWN)
        doc.metadata.title = "Sample Doc"

        md_path = output_dir / "sample.md"
        write_document(doc, md_path)
        print_success(f"  Markdown written to {md_path}")

        csv_data = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
        csv_doc = Document(content=csv_data, format=DocumentFormat.CSV)
        csv_path = output_dir / "data.csv"
        write_document(csv_doc, csv_path)
        print_success(f"  CSV written to {csv_path}")

    except Exception as e:
        print_error(f"  Writing failed: {e}")
        return 1

    # 2. Document Reading
    print_info("Testing document reading and metadata...")
    try:
        read_doc = read_document(md_path)
        print_success(f"  Read document: {read_doc.metadata.title}")
        print_info(f"  Content length: {len(read_doc.get_content_as_string())}")
    except Exception as e:
        print_error(f"  Reading failed: {e}")
        return 1

    # 3. Transformation
    print_info("Testing document transformation...")
    try:
        # Convert MD to HTML (basic)
        html_doc = convert_document(read_doc, DocumentFormat.HTML)
        print_success(
            f"  Converted to HTML. Content starts with: {html_doc.get_content_as_string()[:20]}..."
        )

        # Merge
        merged = merge_documents(
            [read_doc, Document("## Footer", DocumentFormat.MARKDOWN)]
        )
        print_success(
            f"  Merged documents. Total length: {len(merged.get_content_as_string())}"
        )

        # Split
        chunks = split_document(merged, {"method": "by_sections"})
        print_success(f"  Split merged doc into {len(chunks)} sections.")
    except Exception as e:
        print_error(f"  Transformation failed: {e}")
        return 1

    # 4. Search
    print_info("Testing indexing and search...")
    try:
        index = create_index()
        index_document(read_doc, index)

        results = search_documents("Codomyrmex", index)
        print_success(f"  Found {len(results)} matches for 'Codomyrmex'")
    except Exception as e:
        print_error(f"  Search failed: {e}")
        return 1

    print_success("Document basic usage examples completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
