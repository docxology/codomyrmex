#!/usr/bin/env python3
"""
Compression - Real Usage Examples

Demonstrates actual compression capabilities:
- gzip and zlib compression
- Data integrity verification
- File compression utilities
- Archive creation and extraction
- Auto-detection of formats
"""

import sys
import os
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.compression import (
    compress,
    auto_decompress,
    compress_file,
    decompress_file,
    ArchiveManager
)

def main():
    setup_logging()
    print_info("Running Compression Examples...")

    # 1. Byte Compression
    print_info("Testing byte-level compression...")
    try:
        data = b"Hello Codomyrmex Compression " * 100
        original_size = len(data)
        
        # Gzip
        compressed_gz = compress(data, format="gzip")
        print_info(f"  Gzip: {original_size} -> {len(compressed_gz)} bytes")
        
        # Zlib
        compressed_zl = compress(data, format="zlib")
        print_info(f"  Zlib: {original_size} -> {len(compressed_zl)} bytes")
        
        # Auto-decompress
        decompressed = auto_decompress(compressed_gz)
        if decompressed == data:
            print_success("  Auto-decompress (Gzip) successful.")
            
        decompressed = auto_decompress(compressed_zl)
        if decompressed == data:
            print_success("  Auto-decompress (Zlib) successful.")
            
    except Exception as e:
        print_error(f"  Byte compression failed: {e}")

    # 2. File Compression
    print_info("Testing file compression...")
    try:
        test_dir = Path("output/compression_test")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        input_file = test_dir / "test.txt"
        input_file.write_text("This is a test file for compression." * 1000)
        
        # Compress file
        compressed_file = compress_file(str(input_file), format="gzip")
        if os.path.exists(compressed_file):
            print_success(f"  File compressed: {compressed_file}")
            
        # Decompress file
        decompressed_file = decompress_file(compressed_file)
        if os.path.exists(decompressed_file):
            print_success(f"  File decompressed: {decompressed_file}")
            
    except Exception as e:
        print_error(f"  File compression failed: {e}")

    # 3. Archive Management
    print_info("Testing ArchiveManager...")
    try:
        archive_out = test_dir / "test_archive.zip"
        files_to_archive = [input_file]
        
        mgr = ArchiveManager()
        if mgr.create_archive(files_to_archive, archive_out, format="zip"):
            print_success(f"  Archive created: {archive_out}")
            
        extract_dir = test_dir / "extracted"
        if mgr.extract_archive(archive_out, extract_dir):
            print_success(f"  Archive extracted to: {extract_dir}")
            
    except Exception as e:
        print_error(f"  Archive management failed: {e}")

    print_success("Compression examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
