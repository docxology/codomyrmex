#!/usr/bin/env python3
"""
Documentation Link Validation Tool

This script validates internal and external links in documentation files,
identifying broken links and providing suggestions for fixes.
"""

import os
import re
import sys
import requests
import urllib.parse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
SCRIPT_DIR = Path(__file__).parent.parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class LinkValidator:
    """
    Comprehensive link validation tool for documentation.

    Validates internal links (relative paths) and external links (URLs),
    with support for concurrent checking and detailed reporting.
    """

    def __init__(self, base_path: Optional[str] = None, timeout: int = 10, max_workers: int = 5):
        """
        Initialize the link validator.

        Args:
            base_path: Base path for resolving relative links
            timeout: Timeout for external link checks in seconds
            max_workers: Maximum concurrent workers for link checking
        """
        self.base_path = Path(base_path or SCRIPT_DIR)
        self.timeout = timeout
        self.max_workers = max_workers
        self.checked_links: Dict[str, Dict] = {}
        self.session = requests.Session()

        # Configure session for better performance
        self.session.headers.update({
            'User-Agent': 'Codomyrmex-Link-Validator/1.0'
        })

    def validate_all_links(self, doc_path: str) -> Dict[str, List[str]]:
        """
        Validate all links in a documentation path.

        Args:
            doc_path: Path to documentation directory or file

        Returns:
            Dictionary mapping file paths to lists of issues
        """
        doc_path = Path(doc_path)

        if doc_path.is_file():
            files_to_check = [doc_path]
        elif doc_path.is_dir():
            files_to_check = list(doc_path.rglob("*.md")) + list(doc_path.rglob("*.rst"))
        else:
            raise ValueError(f"Path {doc_path} is not a valid file or directory")

        logger.info(f"Found {len(files_to_check)} documentation files to check")

        results = {}

        for file_path in files_to_check:
            try:
                issues = self._validate_file_links(file_path)
                if issues:
                    results[str(file_path)] = issues
            except Exception as e:
                logger.error(f"Error checking links in {file_path}: {e}")
                results[str(file_path)] = [f"Error during validation: {e}"]

        return results

    def check_internal_links(self, doc_path: str) -> List[str]:
        """
        Check internal links within documentation.

        Args:
            doc_path: Path to documentation directory

        Returns:
            List of broken internal link issues
        """
        doc_path = Path(doc_path)
        issues = []

        # Find all markdown files
        md_files = list(doc_path.rglob("*.md"))

        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Find relative links
                relative_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)

                for link_text, link_url in relative_links:
                    if not link_url.startswith(('http://', 'https://', 'mailto:', '#')):
                        # This is a relative link
                        resolved_path = (md_file.parent / link_url).resolve()

                        if not resolved_path.exists():
                            # Check if it's a fragment link (anchor)
                            if '#' in link_url:
                                base_url, fragment = link_url.split('#', 1)
                                if base_url:
                                    resolved_path = (md_file.parent / base_url).resolve()
                                    if not resolved_path.exists():
                                        issues.append(f"{md_file}: Broken internal link '{link_url}'")
                                # Fragment links are harder to validate without parsing HTML
                            else:
                                issues.append(f"{md_file}: Broken internal link '{link_url}'")

            except Exception as e:
                issues.append(f"{md_file}: Error checking links: {e}")

        return issues

    def check_external_links(self, doc_path: str) -> List[str]:
        """
        Check external links in documentation.

        Args:
            doc_path: Path to documentation directory

        Returns:
            List of broken external link issues
        """
        doc_path = Path(doc_path)
        issues = []

        # Find all markdown files
        md_files = list(doc_path.rglob("*.md"))

        # Collect all external links
        external_links = set()

        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Find external links
                links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                for link_text, link_url in links:
                    if link_url.startswith(('http://', 'https://')):
                        external_links.add((link_url, md_file))

            except Exception as e:
                logger.error(f"Error reading {md_file}: {e}")

        logger.info(f"Found {len(external_links)} external links to check")

        # Check external links concurrently
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_link = {
                executor.submit(self._check_external_link, url): (url, file_path)
                for url, file_path in external_links
            }

            for future in as_completed(future_to_link):
                url, file_path = future_to_link[future]
                try:
                    is_broken, error_msg = future.result()
                    if is_broken:
                        issues.append(f"{file_path}: Broken external link '{url}' - {error_msg}")
                except Exception as e:
                    issues.append(f"{file_path}: Error checking link '{url}': {e}")

        return issues

    def fix_broken_links(self, doc_path: str, dry_run: bool = True) -> Dict[str, Any]:
        """
        Attempt to fix broken links automatically.

        Args:
            doc_path: Path to documentation directory
            dry_run: If True, only report what would be fixed

        Returns:
            Dictionary with fix results
        """
        results = {
            "fixed": [],
            "unfixable": [],
            "errors": [],
            "dry_run": dry_run
        }

        # For now, this is a basic implementation
        # Could be enhanced with more sophisticated link fixing logic

        broken_links = self.check_internal_links(doc_path)

        for issue in broken_links:
            if "docs/" in issue and "README.md" in issue:
                # Try to fix common broken doc links
                # This is a placeholder for more sophisticated fixing
                results["unfixable"].append(issue)
            else:
                results["unfixable"].append(issue)

        if not dry_run:
            logger.warning("Automatic link fixing not fully implemented yet")

        return results

    def _validate_file_links(self, file_path: Path) -> List[str]:
        """Validate links in a single file."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Find all markdown links
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)

            for link_text, link_url in links:
                if link_url.startswith(('http://', 'https://')):
                    # External link
                    is_broken, error_msg = self._check_external_link(link_url)
                    if is_broken:
                        issues.append(f"Broken external link '{link_url}': {error_msg}")
                elif not link_url.startswith(('mailto:', '#')):
                    # Internal link
                    resolved_path = (file_path.parent / link_url).resolve()
                    if not resolved_path.exists():
                        issues.append(f"Broken internal link '{link_url}'")

        except Exception as e:
            issues.append(f"Error reading file: {e}")

        return issues

    def _check_external_link(self, url: str) -> Tuple[bool, str]:
        """
        Check if an external link is accessible.

        Args:
            url: URL to check

        Returns:
            Tuple of (is_broken, error_message)
        """
        if url in self.checked_links:
            # Use cached result
            cached = self.checked_links[url]
            return cached["broken"], cached.get("error", "")

        try:
            response = self.session.head(url, timeout=self.timeout, allow_redirects=True)

            # Some servers don't support HEAD, try GET
            if response.status_code == 405:  # Method not allowed
                response = self.session.get(url, timeout=self.timeout, stream=True)
                response.close()

            is_broken = response.status_code >= 400
            error_msg = f"HTTP {response.status_code}" if is_broken else ""

        except requests.exceptions.Timeout:
            is_broken = True
            error_msg = "Timeout"
        except requests.exceptions.ConnectionError:
            is_broken = True
            error_msg = "Connection error"
        except requests.exceptions.RequestException as e:
            is_broken = True
            error_msg = str(e)
        except Exception as e:
            is_broken = True
            error_msg = f"Unexpected error: {e}"

        # Cache result
        self.checked_links[url] = {
            "broken": is_broken,
            "error": error_msg
        }

        return is_broken, error_msg


def validate_all_links(doc_path: str) -> Dict[str, List[str]]:
    """
    Convenience function to validate all links in documentation.

    Args:
        doc_path: Path to documentation directory

    Returns:
        Dictionary mapping file paths to lists of link issues
    """
    validator = LinkValidator()
    return validator.validate_all_links(doc_path)


def check_internal_links(doc_path: str) -> List[str]:
    """
    Convenience function to check internal links.

    Args:
        doc_path: Path to documentation directory

    Returns:
        List of broken internal link issues
    """
    validator = LinkValidator()
    return validator.check_internal_links(doc_path)


def check_external_links(doc_path: str) -> List[str]:
    """
    Convenience function to check external links.

    Args:
        doc_path: Path to documentation directory

    Returns:
        List of broken external link issues
    """
    validator = LinkValidator()
    return validator.check_external_links(doc_path)


def fix_broken_links(doc_path: str, dry_run: bool = True) -> Dict[str, Any]:
    """
    Convenience function to fix broken links.

    Args:
        doc_path: Path to documentation directory
        dry_run: If True, only report what would be fixed

    Returns:
        Dictionary with fix results
    """
    validator = LinkValidator()
    return validator.fix_broken_links(doc_path, dry_run)


def main():
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate documentation links",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --path docs/ --check internal
  %(prog)s --path docs/ --check external
  %(prog)s --path docs/ --fix --dry-run
  %(prog)s --file README.md --validate
        """
    )

    parser.add_argument(
        '--path', '-p',
        default='docs/',
        help='Path to documentation directory (default: docs/)'
    )

    parser.add_argument(
        '--file', '-f',
        help='Specific file to validate'
    )

    parser.add_argument(
        '--check',
        choices=['internal', 'external', 'all'],
        default='all',
        help='Type of links to check (default: all)'
    )

    parser.add_argument(
        '--fix',
        action='store_true',
        help='Attempt to fix broken links'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be fixed without actually fixing'
    )

    parser.add_argument(
        '--timeout',
        type=int,
        default=10,
        help='Timeout for external link checks in seconds (default: 10)'
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=5,
        help='Number of concurrent workers (default: 5)'
    )

    args = parser.parse_args()

    # Determine path to check
    if args.file:
        doc_path = args.file
    else:
        doc_path = args.path

    # Create validator
    validator = LinkValidator(timeout=args.timeout, max_workers=args.workers)

    try:
        if args.fix:
            print("🔧 Attempting to fix broken links...")
            results = validator.fix_broken_links(doc_path, dry_run=args.dry_run)

            if args.dry_run:
                print("📋 Dry run results:")
            else:
                print("✅ Fix results:")

            print(f"  Fixed: {len(results['fixed'])}")
            print(f"  Unfixable: {len(results['unfixable'])}")
            print(f"  Errors: {len(results['errors'])}")

            if results['fixed']:
                print("\nFixed links:")
                for fix in results['fixed']:
                    print(f"  ✅ {fix}")

            if results['unfixable']:
                print("\nUnfixable broken links:")
                for issue in results['unfixable']:
                    print(f"  ❌ {issue}")

        else:
            print("🔍 Checking documentation links...")

            if args.check in ['internal', 'all']:
                print("\n🔗 Checking internal links...")
                internal_issues = validator.check_internal_links(doc_path)
                print(f"Found {len(internal_issues)} internal link issues")

                if internal_issues:
                    for issue in internal_issues[:10]:  # Show first 10
                        print(f"  ❌ {issue}")
                    if len(internal_issues) > 10:
                        print(f"  ... and {len(internal_issues) - 10} more")

            if args.check in ['external', 'all']:
                print("\n🌐 Checking external links...")
                external_issues = validator.check_external_links(doc_path)
                print(f"Found {len(external_issues)} external link issues")

                if external_issues:
                    for issue in external_issues[:10]:  # Show first 10
                        print(f"  ❌ {issue}")
                    if len(external_issues) > 10:
                        print(f"  ... and {len(external_issues) - 10} more")

            if args.check == 'all':
                all_issues = validator.validate_all_links(doc_path)
                total_files = len(all_issues)
                total_issues = sum(len(issues) for issues in all_issues.values())

                print("
📊 Summary:"                print(f"  Files checked: {total_files}")
                print(f"  Total issues: {total_issues}")

                if total_issues == 0:
                    print("  ✅ All links are valid!")
                else:
                    print(f"  ❌ Found issues in {len([f for f, issues in all_issues.items() if issues])} files")

    except Exception as e:
        logger.error(f"Error during link validation: {e}")
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
