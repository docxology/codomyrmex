#!/usr/bin/env python3
"""
Documentation Quality Validation Script

This script performs comprehensive validation of documentation quality
to prevent errors from accumulating across versions.
"""

import hashlib
import os
import re
import sys
from pathlib import Path

# Add project root to path for imports
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))  # Removed sys.path manipulation
from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


class DocumentationValidator:
    """Comprehensive documentation quality validator."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.src_dir = self.project_root / "src" / "codomyrmex"
        self.docs_dir = self.src_dir / "documentation"
        self.aggregated_docs_dir = self.docs_dir / "docs" / "modules"

        # Standard documentation files that should exist
        self.required_files = [
            "README.md",
            "CHANGELOG.md",
            "API_SPECIFICATION.md",
            "USAGE_EXAMPLES.md",
        ]

        self.optional_files = ["MCP_TOOL_SPECIFICATION.md", "SECURITY.md"]

    def validate_module_structure(self) -> list[str]:
        """Validate that all modules have proper documentation structure."""
        issues = []

        for module_dir in sorted(self.src_dir.glob("*/")):
            if not module_dir.is_dir() or module_dir.name.startswith("_"):
                continue

            module_name = module_dir.name
            logger.info(f"Validating module: {module_name}")

            # Check required files
            for required_file in self.required_files:
                file_path = module_dir / required_file
                if not file_path.exists():
                    issues.append(
                        f"Module {module_name}: Missing required file {required_file}"
                    )

            # Check docs/ directory structure
            docs_dir = module_dir / "docs"
            if docs_dir.exists():
                # Check for technical_overview.md
                tech_overview = docs_dir / "technical_overview.md"
                if not tech_overview.exists():
                    issues.append(
                        f"Module {module_name}: Missing docs/technical_overview.md"
                    )

                # Check for tutorials directory
                tutorials_dir = docs_dir / "tutorials"
                if tutorials_dir.exists():
                    tutorial_files = list(tutorials_dir.glob("*.md"))
                    if not tutorial_files:
                        issues.append(
                            f"Module {module_name}: Empty tutorials directory"
                        )
                else:
                    issues.append(
                        f"Module {module_name}: Missing docs/tutorials/ directory"
                    )

        return issues

    def validate_version_consistency(self) -> list[str]:
        """Validate version consistency between source and aggregated docs."""
        issues = []

        for module_dir in sorted(self.src_dir.glob("*/")):
            if not module_dir.is_dir() or module_dir.name.startswith("_"):
                continue

            module_name = module_dir.name
            aggregated_module_dir = self.aggregated_docs_dir / module_name

            if not aggregated_module_dir.exists():
                issues.append(
                    f"Module {module_name}: No aggregated documentation found"
                )
                continue

            # Compare file hashes for critical files
            critical_files = ["CHANGELOG.md", "README.md", "API_SPECIFICATION.md"]

            for filename in critical_files:
                source_file = module_dir / filename
                aggregated_file = aggregated_module_dir / filename

                if source_file.exists() and aggregated_file.exists():
                    source_hash = self._file_hash(source_file)
                    aggregated_hash = self._file_hash(aggregated_file)

                    if source_hash != aggregated_hash:
                        issues.append(
                            f"Module {module_name}: {filename} differs between source and aggregated docs"
                        )

                elif source_file.exists() and not aggregated_file.exists():
                    issues.append(
                        f"Module {module_name}: {filename} exists in source but missing in aggregated docs"
                    )

        return issues

    def validate_changelog_format(self) -> list[str]:
        """Validate CHANGELOG.md format consistency."""
        issues = []

        changelog_pattern = re.compile(r"^## \[\d+\.\d+\.\d+\] - \d{4}-\d{2}-\d{2}")

        for changelog_file in self.src_dir.glob("*/CHANGELOG.md"):
            module_name = changelog_file.parent.name

            try:
                with open(changelog_file) as f:
                    content = f.read()

                lines = content.split("\n")
                version_headers = [line for line in lines if line.startswith("## [")]

                if not version_headers:
                    issues.append(
                        f"Module {module_name}: No version headers found in CHANGELOG.md"
                    )
                    continue

                for header in version_headers:
                    if not changelog_pattern.match(header):
                        issues.append(
                            f"Module {module_name}: Invalid changelog header format: {header}"
                        )

                # Check for unreleased section
                if not any("Unreleased" in line for line in lines):
                    issues.append(
                        f"Module {module_name}: Missing 'Unreleased' section in CHANGELOG.md"
                    )

            except Exception as e:
                issues.append(f"Module {module_name}: Error reading CHANGELOG.md: {e}")

        return issues

    def validate_cross_references(self) -> list[str]:
        """Validate internal cross-references in documentation."""
        issues = []

        for md_file in self.src_dir.glob("**/*.md"):
            try:
                with open(md_file) as f:
                    content = f.read()

                # Find relative links
                relative_links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)

                for _link_text, link_path in relative_links:
                    if not link_path.startswith(("http://", "https://", "#")):
                        # This is a relative link - check if target exists
                        full_path = md_file.parent / link_path
                        if not full_path.exists():
                            issues.append(
                                f"{md_file}: Broken relative link: {link_path}"
                            )

            except Exception as e:
                issues.append(f"Error validating {md_file}: {e}")

        return issues

    def validate_aggregated_docs_freshness(self) -> list[str]:
        """Validate that aggregated docs are not stale."""
        issues = []

        for module_dir in sorted(self.src_dir.glob("*/")):
            if not module_dir.is_dir() or module_dir.name.startswith("_"):
                continue

            module_name = module_dir.name
            aggregated_module_dir = self.aggregated_docs_dir / module_name

            if not aggregated_module_dir.exists():
                continue

            # Check modification times
            for md_file in module_dir.glob("*.md"):
                aggregated_file = aggregated_module_dir / md_file.name

                if aggregated_file.exists():
                    source_mtime = md_file.stat().st_mtime
                    aggregated_mtime = aggregated_file.stat().st_mtime

                    if source_mtime > aggregated_mtime:
                        issues.append(
                            f"Module {module_name}: {md_file.name} is newer than aggregated version"
                        )

        return issues

    def _file_hash(self, file_path: Path) -> str:
        """Calculate file hash for comparison."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def run_full_validation(self) -> tuple[bool, dict[str, list[str]]]:
        """Run all validation checks."""
        logger.info("Starting comprehensive documentation validation...")

        validation_results = {
            "structure": self.validate_module_structure(),
            "version_consistency": self.validate_version_consistency(),
            "changelog_format": self.validate_changelog_format(),
            "cross_references": self.validate_cross_references(),
            "freshness": self.validate_aggregated_docs_freshness(),
        }

        # Count total issues
        total_issues = sum(len(issues) for issues in validation_results.values())
        is_valid = total_issues == 0

        # Log results
        if is_valid:
            logger.info("✓ All documentation validation checks passed!")
        else:
            logger.error(f"✗ Found {total_issues} documentation issues:")

            for check_name, issues in validation_results.items():
                if issues:
                    logger.error(f"  {check_name.upper()} ISSUES:")
                    for issue in issues:
                        logger.error(f"    - {issue}")

        return is_valid, validation_results


def main():
    """Main entry point."""
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )

    validator = DocumentationValidator(project_root)
    is_valid, results = validator.run_full_validation()

    if not is_valid:
        sys.exit(1)


if __name__ == "__main__":
    main()
