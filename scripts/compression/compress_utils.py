#!/usr/bin/env python3
"""
Data compression and decompression utilities.

Usage:
    python compress_utils.py <command> <file> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import gzip
import zipfile
import tarfile


def format_size(size: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def compress_gzip(input_path: Path, output_path: Path = None) -> dict:
    """Compress file with gzip."""
    output = output_path or input_path.with_suffix(input_path.suffix + ".gz")
    
    with open(input_path, "rb") as f_in:
        with gzip.open(output, "wb") as f_out:
            f_out.write(f_in.read())
    
    original = input_path.stat().st_size
    compressed = output.stat().st_size
    
    return {
        "output": str(output),
        "original_size": original,
        "compressed_size": compressed,
        "ratio": compressed / original if original > 0 else 0
    }


def decompress_gzip(input_path: Path, output_path: Path = None) -> dict:
    """Decompress gzip file."""
    output = output_path or input_path.with_suffix("").with_suffix(input_path.stem.split(".")[-1] if "." in input_path.stem else "")
    if str(output) == str(input_path):
        output = input_path.with_suffix(".decompressed")
    
    with gzip.open(input_path, "rb") as f_in:
        with open(output, "wb") as f_out:
            f_out.write(f_in.read())
    
    return {"output": str(output), "size": output.stat().st_size}


def analyze_archive(path: Path) -> dict:
    """Analyze archive contents."""
    info = {"type": "unknown", "files": 0, "total_size": 0}
    
    suffix = path.suffix.lower()
    
    if suffix == ".zip":
        with zipfile.ZipFile(path) as zf:
            info["type"] = "zip"
            info["files"] = len(zf.namelist())
            info["total_size"] = sum(i.file_size for i in zf.infolist())
            info["contents"] = zf.namelist()[:10]
    
    elif suffix in [".tar", ".gz", ".tgz", ".bz2"]:
        mode = "r:*"
        with tarfile.open(path, mode) as tf:
            info["type"] = "tar"
            members = tf.getmembers()
            info["files"] = len(members)
            info["total_size"] = sum(m.size for m in members)
            info["contents"] = [m.name for m in members[:10]]
    
    return info


def main():
    parser = argparse.ArgumentParser(description="Compression utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # Compress command
    comp = subparsers.add_parser("compress", help="Compress a file")
    comp.add_argument("file", help="File to compress")
    comp.add_argument("--output", "-o", help="Output file")
    comp.add_argument("--format", "-f", choices=["gzip", "bz2"], default="gzip")
    
    # Decompress command
    decomp = subparsers.add_parser("decompress", help="Decompress a file")
    decomp.add_argument("file", help="File to decompress")
    decomp.add_argument("--output", "-o", help="Output file")
    
    # Analyze command
    analyze = subparsers.add_parser("analyze", help="Analyze archive")
    analyze.add_argument("file", help="Archive file")
    
    args = parser.parse_args()
    
    if not args.command:
        print("🗜️  Compression Utilities\n")
        print("Commands:")
        print("  compress   - Compress a file (gzip/bz2)")
        print("  decompress - Decompress a file")
        print("  analyze    - Analyze archive contents")
        return 0
    
    if args.command == "compress":
        path = Path(args.file)
        if not path.exists():
            print(f"❌ File not found: {args.file}")
            return 1
        
        output = Path(args.output) if args.output else None
        result = compress_gzip(path, output)
        
        print(f"🗜️  Compressed: {path.name}\n")
        print(f"   Output: {result['output']}")
        print(f"   Original: {format_size(result['original_size'])}")
        print(f"   Compressed: {format_size(result['compressed_size'])}")
        print(f"   Ratio: {result['ratio']:.1%}")
    
    elif args.command == "decompress":
        path = Path(args.file)
        if not path.exists():
            print(f"❌ File not found: {args.file}")
            return 1
        
        output = Path(args.output) if args.output else None
        result = decompress_gzip(path, output)
        
        print(f"📦 Decompressed: {path.name}\n")
        print(f"   Output: {result['output']}")
        print(f"   Size: {format_size(result['size'])}")
    
    elif args.command == "analyze":
        path = Path(args.file)
        if not path.exists():
            print(f"❌ File not found: {args.file}")
            return 1
        
        info = analyze_archive(path)
        print(f"📦 Archive: {path.name}\n")
        print(f"   Type: {info['type']}")
        print(f"   Files: {info['files']}")
        print(f"   Total size: {format_size(info['total_size'])}")
        if info.get("contents"):
            print("   Contents:")
            for c in info["contents"]:
                print(f"      - {c}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
