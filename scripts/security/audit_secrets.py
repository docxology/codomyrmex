#!/usr/bin/env python3
"""
Scan repository for accidentally committed secrets and sensitive data.

Usage:
    python audit_secrets.py [--path PATH] [--verbose] [--fix]
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import re
import os


# Patterns for detecting secrets
SECRET_PATTERNS = {
    "AWS Access Key": r'AKIA[0-9A-Z]{16}',
    "AWS Secret Key": r'(?i)aws(.{0,20})?(?-i)[\'"][0-9a-zA-Z/+]{40}[\'"]',
    "GitHub Token": r'gh[ps]_[a-zA-Z0-9]{36}',
    "GitHub OAuth": r'gho_[a-zA-Z0-9]{36}',
    "Generic API Key": r'(?i)(api[_-]?key|apikey)[\'"\s]*[:=][\'"\s]*[a-zA-Z0-9_-]{20,}',
    "Generic Secret": r'(?i)(secret|password|passwd|pwd)[\'"\s]*[:=][\'"\s]*[^\s\'"]{8,}',
    "Private Key": r'-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----',
    "Slack Token": r'xox[baprs]-[0-9]{10,13}-[a-zA-Z0-9-]+',
    "Stripe Key": r'sk_live_[a-zA-Z0-9]{24}',
    "Google API Key": r'AIza[0-9A-Za-z-_]{35}',
    "JSON Web Token": r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*',
    "Basic Auth": r'(?i)basic\s+[a-zA-Z0-9+/]+={0,2}',
    "Bearer Token": r'(?i)bearer\s+[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+',
    "Database URL": r'(?i)(mysql|postgres|mongodb|redis)://[^\'"\s]+:[^\'"\s]+@',
    "SSH DSA Private Key": r'-----BEGIN DSA PRIVATE KEY-----',
    "SSH RSA Private Key": r'-----BEGIN RSA PRIVATE KEY-----',
    "PEM Certificate": r'-----BEGIN CERTIFICATE-----',
}

# Files/directories to skip
SKIP_PATTERNS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".env.example",
    ".env.sample",
    "package-lock.json",
    "yarn.lock",
    "*.min.js",
    "*.min.css",
}

# File extensions to scan
SCAN_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rb", ".php",
    ".yml", ".yaml", ".json", ".xml", ".env", ".sh", ".bash", ".zsh",
    ".conf", ".config", ".ini", ".properties", ".toml",
    ".md", ".txt", ".rst",
}


def should_skip(path: Path) -> bool:
    """Check if path should be skipped."""
    for part in path.parts:
        if part in SKIP_PATTERNS:
            return True
        for pattern in SKIP_PATTERNS:
            if "*" in pattern and Path(part).match(pattern):
                return True
    return False


def scan_file(file_path: Path) -> list:
    """Scan a file for secrets."""
    findings = []
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            lines = content.split("\n")
    except Exception:
        return findings
    
    for pattern_name, pattern in SECRET_PATTERNS.items():
        for i, line in enumerate(lines, 1):
            # Skip comments in code
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("//"):
                # But still check for actual secrets even in comments
                pass
            
            matches = re.findall(pattern, line)
            for match in matches:
                # Skip example/placeholder values
                match_str = match if isinstance(match, str) else str(match)
                if any(x in match_str.lower() for x in ["example", "placeholder", "xxx", "your_", "replace"]):
                    continue
                
                findings.append({
                    "file": str(file_path),
                    "line": i,
                    "type": pattern_name,
                    "match": match_str[:50] + ("..." if len(match_str) > 50 else ""),
                    "context": line.strip()[:80]
                })
    
    return findings


def scan_directory(path: str, extensions: set = SCAN_EXTENSIONS) -> list:
    """Recursively scan directory for secrets."""
    findings = []
    root = Path(path)
    
    for file_path in root.rglob("*"):
        if file_path.is_file():
            if should_skip(file_path):
                continue
            
            if extensions and file_path.suffix.lower() not in extensions and file_path.name != ".env":
                continue
            
            file_findings = scan_file(file_path)
            findings.extend(file_findings)
    
    return findings


def check_gitignore(path: str) -> list:
    """Check if sensitive files are in .gitignore."""
    warnings = []
    gitignore = Path(path) / ".gitignore"
    
    sensitive_patterns = [".env", "*.pem", "*.key", "secrets.json", "credentials.json"]
    
    if gitignore.exists():
        with open(gitignore, "r") as f:
            content = f.read()
        
        for pattern in sensitive_patterns:
            if pattern not in content:
                warnings.append(f"Consider adding '{pattern}' to .gitignore")
    else:
        warnings.append(".gitignore file not found")
    
    return warnings


def main():
    parser = argparse.ArgumentParser(description="Audit repository for secrets")
    parser.add_argument("--path", "-p", default=".", help="Path to scan (default: current directory)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all scanned files")
    parser.add_argument("--all-files", "-a", action="store_true", help="Scan all file types")
    args = parser.parse_args()
    
    path = os.path.abspath(args.path)
    print(f"🔐 Secret Audit: {path}\n")
    
    # Check .gitignore
    gitignore_warnings = check_gitignore(path)
    if gitignore_warnings:
        print("📋 .gitignore recommendations:")
        for w in gitignore_warnings:
            print(f"   ⚠️  {w}")
        print()
    
    # Scan for secrets
    print("🔍 Scanning for secrets...")
    extensions = None if args.all_files else SCAN_EXTENSIONS
    findings = scan_directory(path, extensions)
    
    if findings:
        print(f"\n⚠️  Found {len(findings)} potential secrets:\n")
        
        # Group by file
        by_file = {}
        for f in findings:
            if f["file"] not in by_file:
                by_file[f["file"]] = []
            by_file[f["file"]].append(f)
        
        for file_path, file_findings in by_file.items():
            rel_path = os.path.relpath(file_path, path)
            print(f"📄 {rel_path}")
            for f in file_findings:
                print(f"   Line {f['line']}: {f['type']}")
                if args.verbose:
                    print(f"      Context: {f['context']}")
            print()
        
        print("🔧 Recommendations:")
        print("   1. Remove secrets from code and use environment variables")
        print("   2. If committed to git, rotate the exposed credentials immediately")
        print("   3. Use git-filter-branch or BFG to remove from history if needed")
        print("   4. Add sensitive file patterns to .gitignore")
        
        return 1
    else:
        print("\n✅ No secrets detected")
        print("   Scanned file types:", ", ".join(sorted(SCAN_EXTENSIONS)[:8]), "...")
        return 0


if __name__ == "__main__":
    sys.exit(main())
