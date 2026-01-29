#!/usr/bin/env python3
"""
Document management utilities.

Usage:
    python doc_utils.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import re
from datetime import datetime


def analyze_document(path: Path) -> dict:
    """Analyze a document."""
    content = path.read_text()
    lines = content.split("\n")
    
    info = {
        "path": str(path),
        "size": len(content),
        "lines": len(lines),
        "words": len(content.split()),
        "headings": 0,
        "links": 0,
        "code_blocks": 0,
    }
    
    if path.suffix == ".md":
        info["headings"] = len(re.findall(r'^#{1,6}\s', content, re.MULTILINE))
        info["links"] = len(re.findall(r'\[.+?\]\(.+?\)', content))
        info["code_blocks"] = len(re.findall(r'```', content)) // 2
    
    return info


def find_documents(path: str, extensions: list = None) -> list:
    """Find documents in path."""
    exts = extensions or [".md", ".txt", ".rst", ".adoc"]
    p = Path(path)
    
    found = []
    for ext in exts:
        found.extend(p.rglob(f"*{ext}"))
    
    return [f for f in found if "node_modules" not in str(f) and "__pycache__" not in str(f)]


def check_frontmatter(path: Path) -> dict:
    """Check for frontmatter in markdown."""
    content = path.read_text()
    
    result = {"has_frontmatter": False, "fields": []}
    
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            result["has_frontmatter"] = True
            for line in parts[1].split("\n"):
                if ":" in line:
                    key = line.split(":")[0].strip()
                    if key:
                        result["fields"].append(key)
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Document utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # Find command
    find = subparsers.add_parser("find", help="Find documents")
    find.add_argument("path", nargs="?", default=".")
    
    # Analyze command
    analyze = subparsers.add_parser("analyze", help="Analyze document")
    analyze.add_argument("path", help="Document path")
    
    # Stats command
    stats = subparsers.add_parser("stats", help="Document statistics")
    stats.add_argument("path", nargs="?", default=".")
    
    args = parser.parse_args()
    
    if not args.command:
        print("📄 Document Utilities\n")
        print("Commands:")
        print("  find    - Find documents")
        print("  analyze - Analyze a document")
        print("  stats   - Get document statistics")
        return 0
    
    if args.command == "find":
        docs = find_documents(args.path)
        print(f"📚 Documents ({len(docs)}):\n")
        
        by_ext = {}
        for d in docs:
            ext = d.suffix
            by_ext.setdefault(ext, []).append(d)
        
        for ext, files in sorted(by_ext.items()):
            print(f"   {ext}: {len(files)} files")
            for f in files[:3]:
                print(f"      - {f.name}")
    
    elif args.command == "analyze":
        path = Path(args.path)
        if not path.exists():
            print(f"❌ File not found: {args.path}")
            return 1
        
        info = analyze_document(path)
        fm = check_frontmatter(path) if path.suffix == ".md" else None
        
        print(f"📄 Document: {path.name}\n")
        print(f"   Lines: {info['lines']}")
        print(f"   Words: {info['words']}")
        if info['headings']:
            print(f"   Headings: {info['headings']}")
        if info['links']:
            print(f"   Links: {info['links']}")
        if fm and fm["has_frontmatter"]:
            print(f"   Frontmatter: {', '.join(fm['fields'])}")
    
    elif args.command == "stats":
        docs = find_documents(args.path)
        
        total_words = 0
        total_lines = 0
        
        for d in docs:
            try:
                content = d.read_text()
                total_words += len(content.split())
                total_lines += len(content.split("\n"))
            except:
                pass
        
        print(f"📊 Document Statistics:\n")
        print(f"   Documents: {len(docs)}")
        print(f"   Total words: {total_words:,}")
        print(f"   Total lines: {total_lines:,}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
