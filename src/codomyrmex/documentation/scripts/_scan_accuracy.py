"""Phase 2: Accuracy Verification for Documentation Scan."""

import re
import subprocess
from collections import defaultdict
from typing import TYPE_CHECKING

from codomyrmex.logging_monitoring import get_logger

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any

logger = get_logger(__name__)


class DocumentationAccuracyMixin:
    """Phase 2: Accuracy Verification"""

    repo_root: "Path"
    results: "dict[str, Any]"

    def phase2_accuracy(self):
        """Phase 2: Accuracy Verification"""
        print("=" * 80)
        print("PHASE 2: ACCURACY VERIFICATION")
        print("=" * 80)
        print()

        # 2.1 Content Accuracy
        print("2.1 Checking content accuracy...")
        content_issues = self._check_content_accuracy()
        self.results["phase2"]["content_issues"] = content_issues
        print(f"  ✓ Found {len(content_issues)} content accuracy issues")
        print()

        # 2.2 Reference Accuracy
        print("2.2 Validating references...")
        reference_issues = self._check_reference_accuracy()
        self.results["phase2"]["reference_issues"] = reference_issues
        print(f"  ✓ Found {len(reference_issues)} reference issues")
        print()

        # 2.3 Terminology Consistency
        print("2.3 Checking terminology consistency...")
        terminology_issues = self._check_terminology_consistency()
        self.results["phase2"]["terminology_issues"] = terminology_issues
        print(f"  ✓ Found {len(terminology_issues)} terminology issues")
        print()

        print("✓ Phase 2 complete!")
        print()
        return self.results["phase2"]

    def _check_content_accuracy(self) -> list[dict]:
        """Check content accuracy in documentation."""
        issues = []

        # Check version numbers in main README
        readme_path = self.repo_root / "README.md"
        if readme_path.exists():
            content = readme_path.read_text(encoding="utf-8")
            # Look for version references
            version_pattern = r"v?(\d+\.\d+\.\d+)"
            versions = re.findall(version_pattern, content)
            if versions:
                # Check if version matches pyproject.toml
                pyproject_path = self.repo_root / "pyproject.toml"
                if pyproject_path.exists():
                    pyproject_content = pyproject_path.read_text(encoding="utf-8")
                    pyproject_version = re.search(
                        r'version\s*=\s*["\']([^"\']+)["\']', pyproject_content
                    )
                    if pyproject_version:
                        pyproject_ver = pyproject_version.group(1)
                        # Check if versions are consistent
                        if pyproject_ver not in versions:
                            issues.append(
                                {
                                    "type": "version_mismatch",
                                    "file": "README.md",
                                    "issue": f"Version in README may not match pyproject.toml ({pyproject_ver})",
                                }
                            )

        return issues

    def _check_reference_accuracy(self) -> list[dict]:
        """Check reference accuracy using existing tools."""
        issues = []

        # Try to run existing link checker
        link_checker = (
            self.repo_root / "scripts" / "documentation" / "check_doc_links.py"
        )
        if link_checker.exists():
            try:
                result = subprocess.run(
                    ["python3", str(link_checker)],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if result.returncode != 0:
                    # Parse output for broken links
                    for line in result.stdout.split("\n"):
                        if "broken" in line.lower() or "error" in line.lower():
                            issues.append(
                                {"type": "broken_link", "details": line.strip()}
                            )
            except Exception as e:
                issues.append(
                    {
                        "type": "tool_error",
                        "tool": "check_doc_links.py",
                        "error": str(e),
                    }
                )

        return issues

    def _check_terminology_consistency(self) -> list[dict]:
        """Check terminology consistency across documentation."""
        issues = []

        # Key terms to check
        key_terms = {
            "codomyrmex": ["Codomyrmex", "codomyrmex", "CODOMYRMEX"],
            "mcp": ["MCP", "Model Context Protocol", "model context protocol"],
            "llm": ["LLM", "Large Language Model", "large language model"],
        }

        # Scan all markdown files for term usage
        all_md_files = list(self.repo_root.rglob("*.md"))
        term_usage = defaultdict(list)

        for md_file in all_md_files[:100]:  # Sample first 100 files
            try:
                content = md_file.read_text(encoding="utf-8")
                for term_group in key_terms.values():
                    for term in term_group:
                        if term.lower() in content.lower():
                            term_usage[term].append(
                                str(md_file.relative_to(self.repo_root))
                            )
            except Exception as e:
                logger.warning("Failed to read markdown file %s: %s", md_file, e)

        # Check for inconsistent usage
        for term_group_name, term_variants in key_terms.items():
            variants_used = [v for v in term_variants if term_usage.get(v, [])]
            if len(variants_used) > 1:
                issues.append(
                    {
                        "type": "terminology_inconsistency",
                        "term": term_group_name,
                        "variants_found": variants_used,
                    }
                )

        return issues
