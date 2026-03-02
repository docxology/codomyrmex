#!/usr/bin/env python3
"""
General utility functions.

Usage:
    python general_utils.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import uuid
import hashlib
import re
from datetime import datetime


def generate_uuid(version: int = 4) -> str:
    """Generate UUID."""
    if version == 4:
        return str(uuid.uuid4())
    elif version == 1:
        return str(uuid.uuid1())
    return str(uuid.uuid4())


def hash_string(text: str, algorithm: str = "sha256") -> str:
    """Hash a string."""
    h = hashlib.new(algorithm)
    h.update(text.encode())
    return h.hexdigest()


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def format_timestamp(timestamp: float = None, fmt: str = "iso") -> str:
    """Format timestamp."""
    dt = datetime.fromtimestamp(timestamp) if timestamp else datetime.now()
    
    formats = {
        "iso": "%Y-%m-%dT%H:%M:%S",
        "date": "%Y-%m-%d",
        "time": "%H:%M:%S",
        "human": "%B %d, %Y at %I:%M %p",
        "file": "%Y%m%d_%H%M%S",
    }
    
    return dt.strftime(formats.get(fmt, fmt))


def count_words(text: str) -> dict:
    """Count words in text."""
    words = re.findall(r'\w+', text.lower())
    return {
        "total": len(words),
        "unique": len(set(words)),
        "chars": len(text),
        "lines": len(text.split("\n")),
    }


def main():
    parser = argparse.ArgumentParser(description="General utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # UUID command
    uuid_cmd = subparsers.add_parser("uuid", help="Generate UUID")
    uuid_cmd.add_argument("--count", "-n", type=int, default=1)
    
    # Hash command
    hash_cmd = subparsers.add_parser("hash", help="Hash string")
    hash_cmd.add_argument("text", help="Text to hash")
    hash_cmd.add_argument("--algo", "-a", default="sha256")
    
    # Slug command
    slug_cmd = subparsers.add_parser("slug", help="Create URL slug")
    slug_cmd.add_argument("text", help="Text to slugify")
    
    # Time command
    time_cmd = subparsers.add_parser("time", help="Format timestamp")
    time_cmd.add_argument("--format", "-f", default="iso")
    
    # Count command
    count_cmd = subparsers.add_parser("count", help="Count words")
    count_cmd.add_argument("file", help="File to count")
    
    args = parser.parse_args()
    
    if not args.command:
        print("🔧 General Utilities\n")
        print("Commands:")
        print("  uuid  - Generate UUID")
        print("  hash  - Hash a string")
        print("  slug  - Create URL slug")
        print("  time  - Format timestamp")
        print("  count - Count words in file")
        return 0
    
    if args.command == "uuid":
        print(f"🆔 UUID(s):\n")
        for _ in range(args.count):
            print(f"   {generate_uuid()}")
    
    elif args.command == "hash":
        result = hash_string(args.text, args.algo)
        print(f"🔒 Hash ({args.algo}):\n   {result}")
    
    elif args.command == "slug":
        result = slugify(args.text)
        print(f"🔗 Slug: {result}")
    
    elif args.command == "time":
        formats = ["iso", "date", "time", "human", "file"]
        print("🕐 Timestamps:\n")
        for fmt in formats:
            print(f"   {fmt:<8}: {format_timestamp(fmt=fmt)}")
    
    elif args.command == "count":
        path = Path(args.file)
        if not path.exists():
            print(f"❌ File not found: {args.file}")
            return 1
        
        stats = count_words(path.read_text())
        print(f"📊 Word count: {path.name}\n")
        print(f"   Words: {stats['total']:,}")
        print(f"   Unique: {stats['unique']:,}")
        print(f"   Characters: {stats['chars']:,}")
        print(f"   Lines: {stats['lines']:,}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
