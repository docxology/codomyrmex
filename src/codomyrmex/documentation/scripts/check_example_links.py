from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import argparse
import json
import logging
import os
import re
import sys

from urllib.parse import urlparse
import requests

from codomyrmex.logging_monitoring import get_logger




























#!/usr/bin/env python3
"""
Link Checker for Codomyrmex Examples Documentation

This script validates all links in README.md files and other documentation
within the examples directory. It checks both internal file references and
external URLs.

Usage:
    python scripts/examples/check_example_links.py

Options:
    --check-external: Also check external URLs (may be slow)
    --verbose: Show detailed checking progress
    --fix: Attempt to fix broken internal links automatically

Output:
    - List of broken links with locations
    - Summary of link health
    - Suggestions for fixes
"""


try:
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    logger = get_logger(__name__)
except ImportError:
    # Fallback logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class LinkChecker:
    """Checks links in Codomyrmex examples documentation."""

    def __init__(self, project_root: Path):
        """Initialize the link checker."""
        self.project_root = project_root
        self.examples_dir = project_root / "examples"

        # Link checking results
        self.results = {
            "total_files_checked": 0,
            "total_links_found": 0,
            "broken_internal_links": [],
            "broken_external_links": [],
            "valid_links": 0,
            "skipped_external": 0,
            "file_results": {}
        }

        # Common file extensions for documentation
        self.doc_extensions = {'.md', '.rst', '.txt'}

    def check_all_links(self, check_external: bool = False, verbose: bool = False, fix: bool = False) -> Dict[str, any]:
        """Check all links in documentation files."""
        logger.info("Starting link validation...")

        if check_external and not REQUESTS_AVAILABLE:
            logger.warning("requests library not available. External link checking will be skipped.")
            check_external = False

        # Find all documentation files
        doc_files = self._find_doc_files()

        self.results["total_files_checked"] = len(doc_files)

        for doc_file in doc_files:
            result = self._check_file_links(doc_file, check_external, verbose)
            self.results["file_results"][str(doc_file)] = result

            self.results["total_links_found"] += result["total_links"]
            self.results["valid_links"] += result["valid_links"]
            self.results["broken_internal_links"].extend(result["broken_internal"])
            self.results["broken_external_links"].extend(result["broken_external"])
            self.results["skipped_external"] += result["skipped_external"]

        # Attempt fixes if requested
        if fix and self.results["broken_internal_links"]:
            self._attempt_fixes(verbose)

        # Calculate summary
        total_broken = len(self.results["broken_internal_links"]) + len(self.results["broken_external_links"])
        self.results["success_rate"] = (
            (self.results["valid_links"] / self.results["total_links_found"] * 100)
            if self.results["total_links_found"] > 0 else 100
        )

        logger.info(f"Link checking complete. Found {total_broken} broken links.")
        return self.results

    def _find_doc_files(self) -> List[Path]:
        """Find all documentation files in examples directory."""
        doc_files = []

        if not self.examples_dir.exists():
            logger.error(f"Examples directory not found: {self.examples_dir}")
            return doc_files

        # Find README.md files and other documentation
        for pattern in ["README.md", "*.md"]:
            for doc_file in self.examples_dir.rglob(pattern):
                # Skip files in hidden directories or specific excludes
                if any(part.startswith('.') or part in ['__pycache__', 'node_modules']
                       for part in doc_file.parts):
                    continue
                doc_files.append(doc_file)

        logger.info(f"Found {len(doc_files)} documentation files")
        return doc_files

    def _check_file_links(self, file_path: Path, check_external: bool, verbose: bool) -> Dict[str, any]:
        """Check all links in a single file."""
        result = {
            "file": str(file_path),
            "total_links": 0,
            "valid_links": 0,
            "broken_internal": [],
            "broken_external": [],
            "skipped_external": 0
        }

        if verbose:
            logger.info(f"Checking links in: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return result

        # Find all markdown links
        links = self._extract_markdown_links(content, file_path)

        result["total_links"] = len(links)

        for link_text, link_url, line_num in links:
            if self._is_external_link(link_url):
                if check_external:
                    if self._check_external_link(link_url):
                        result["valid_links"] += 1
                    else:
                        result["broken_external"].append({
                            "file": str(file_path),
                            "line": line_num,
                            "text": link_text,
                            "url": link_url
                        })
                else:
                    result["skipped_external"] += 1
            else:
                if self._check_internal_link(link_url, file_path):
                    result["valid_links"] += 1
                else:
                    result["broken_internal"].append({
                        "file": str(file_path),
                        "line": line_num,
                        "text": link_text,
                        "url": link_url
                    })

        if verbose:
            valid_count = result["valid_links"]
            broken_count = len(result["broken_internal"]) + len(result["broken_external"])
            logger.info(f"  {valid_count} valid, {broken_count} broken links")

        return result

    def _extract_markdown_links(self, content: str, file_path: Path) -> List[Tuple[str, str, int]]:
        """Extract all markdown links from content."""
        links = []

        # Regular expressions for different link formats
        link_patterns = [
            # [text](url) format
            r'\[([^\]]+)\]\(([^)]+)\)',
            # [text]: url format (reference links)
            r'^\[([^\]]+)\]:\s*(.+)$',
            # <url> format
            r'<([^>]+)>',
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern in link_patterns:
                matches = re.finditer(pattern, line, re.MULTILINE)
                for match in matches:
                    if len(match.groups()) >= 2:
                        link_text = match.group(1)
                        link_url = match.group(2).strip()

                        # Skip code blocks and inline code
                        if self._is_in_code_block(line, match.start()):
                            continue

                        links.append((link_text, link_url, line_num))

        return links

    def _is_in_code_block(self, line: str, match_pos: int) -> bool:
        """Check if a match is inside a code block or inline code."""
        # Simple check - count backticks before the match
        before_match = line[:match_pos]
        backtick_count = before_match.count('`')

        # If odd number of backticks, we're inside inline code
        return backtick_count % 2 == 1

    def _is_external_link(self, url: str) -> bool:
        """Check if a URL is external (has scheme)."""
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.scheme in ['http', 'https', 'ftp', 'mailto'])

    def _check_internal_link(self, url: str, source_file: Path) -> bool:
        """Check if an internal link is valid."""
        # Remove fragment identifiers (#anchor)
        url_without_fragment = url.split('#')[0]

        if not url_without_fragment:
            # Link is just a fragment, which is OK
            return True

        # Resolve the path relative to the source file's directory
        try:
            # Handle relative paths
            if url_without_fragment.startswith('./') or url_without_fragment.startswith('../'):
                resolved_path = (source_file.parent / url_without_fragment).resolve()
            elif url_without_fragment.startswith('/'):
                # Absolute path within project
                resolved_path = (self.project_root / url_without_fragment[1:]).resolve()
            else:
                # Relative to current directory
                resolved_path = (source_file.parent / url_without_fragment).resolve()

            # Check if the file exists
            return resolved_path.exists()

        except Exception:
            return False

    def _check_external_link(self, url: str) -> bool:
        """Check if an external link is accessible."""
        try:
            # Only check HTTP/HTTPS links
            if not url.startswith(('http://', 'https://')):
                return True  # Assume other schemes are OK

            response = requests.head(url, timeout=10, allow_redirects=True)
            return response.status_code < 400

        except Exception:
            return False

    def _attempt_fixes(self, verbose: bool = False):
        """Attempt to fix broken internal links automatically."""
        logger.info("Attempting to fix broken internal links...")

        fixes_applied = 0

        for broken_link in self.results["broken_internal_links"]:
            file_path = Path(broken_link["file"])
            url = broken_link["url"]

            # Try common fixes
            fixed_url = self._suggest_link_fix(url, file_path)

            if fixed_url and fixed_url != url:
                if self._apply_link_fix(file_path, broken_link["line"], url, fixed_url):
                    fixes_applied += 1
                    if verbose:
                        logger.info(f"Fixed link in {file_path}: {url} -> {fixed_url}")

        logger.info(f"Applied {fixes_applied} automatic fixes")

    def _suggest_link_fix(self, url: str, source_file: Path) -> Optional[str]:
        """Suggest a fix for a broken link."""
        # Common fix patterns
        fixes = [
            # Add missing .md extension
            lambda u: u + '.md' if not u.endswith('.md') and not u.endswith('/') and '.' not in u else None,

            # Fix common path issues
            lambda u: u.replace('docs/', '../../docs/') if u.startswith('docs/') else None,
            lambda u: u.replace('testing/', '../../testing/') if u.startswith('testing/') else None,

            # Fix case sensitivity issues (basic)
            lambda u: u.lower() if u != u.lower() else None,
        ]

        for fix_func in fixes:
            suggestion = fix_func(url)
            if suggestion and self._check_internal_link(suggestion, source_file):
                return suggestion

        return None

    def _apply_link_fix(self, file_path: Path, line_num: int, old_url: str, new_url: str) -> bool:
        """Apply a link fix to a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if line_num <= len(lines):
                line = lines[line_num - 1]
                # Simple replacement - this is basic and might need refinement
                new_line = line.replace(f']({old_url})', f']({new_url})')
                new_line = new_line.replace(f']: {old_url}', f']: {new_url}')

                lines[line_num - 1] = new_line

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)

                return True

        except Exception as e:
            logger.error(f"Failed to apply fix to {file_path}: {e}")

        return False

    def print_report(self, results: Dict[str, any], verbose: bool = False):
        """Print link checking results."""
        print("\n" + "="*80)
        print("🔗 LINK VALIDATION REPORT")
        print("="*80)

        print(f"\n📊 SUMMARY:")
        print(f"   Files Checked: {results['total_files_checked']}")
        print(f"   Links Found: {results['total_links_found']}")
        print(f"   Valid Links: {results['valid_links']}")
        print(f"   Broken Internal: {len(results['broken_internal_links'])}")
        print(f"   Broken External: {len(results['broken_external_links'])}")
        print(f"   Skipped External: {results['skipped_external']}")
        print(f"   Success Rate: {results['success_rate']:.1f}%")

        if results['broken_internal_links']:
            print(f"\n❌ BROKEN INTERNAL LINKS ({len(results['broken_internal_links'])}):")
            for link in results['broken_internal_links'][:10]:  # Show first 10
                print(f"   • {link['file']}:{link['line']} - {link['text']} -> {link['url']}")
            if len(results['broken_internal_links']) > 10:
                print(f"   ... and {len(results['broken_internal_links']) - 10} more")

        if results['broken_external_links']:
            print(f"\n🌐 BROKEN EXTERNAL LINKS ({len(results['broken_external_links'])}):")
            for link in results['broken_external_links'][:5]:  # Show first 5
                print(f"   • {link['file']}:{link['line']} - {link['text']} -> {link['url']}")
            if len(results['broken_external_links']) > 5:
                print(f"   ... and {len(results['broken_external_links']) - 5} more")

        print(f"\n✅ REPORT GENERATED")
        print("="*80)

    def save_report(self, results: Dict[str, any], output_file: str = None):
        """Save link checking results to file."""
        if output_file is None:
            output_file = self.project_root / "examples" / "link_check_report.json"

        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"Report saved to: {output_file}")


def main():
    """Main function to run link checking."""
    parser = argparse.ArgumentParser(description="Check links in Codomyrmex examples documentation")
    parser.add_argument("--check-external", action="store_true", help="Also check external URLs")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed checking progress")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix broken internal links automatically")
    parser.add_argument("--output", "-o", help="Output file for link check report")

    args = parser.parse_args()

    checker = LinkChecker(project_root)

    # Run link checking
    results = checker.check_all_links(
        check_external=args.check_external,
        verbose=args.verbose,
        fix=args.fix
    )

    # Print report
    checker.print_report(results, verbose=args.verbose)

    # Save report
    checker.save_report(results, args.output)

    # Exit with appropriate code
    total_broken = len(results["broken_internal_links"]) + len(results["broken_external_links"])
    if total_broken > 0:
        logger.warning(f"Found {total_broken} broken links")
        sys.exit(1)
    else:
        logger.info("All links are valid! 🎉")
        sys.exit(0)


if __name__ == "__main__":
    main()
