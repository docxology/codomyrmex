"""Phase 4: Quality Assessment for Documentation Scan."""

from typing import TYPE_CHECKING

from codomyrmex.logging_monitoring import get_logger

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any

logger = get_logger(__name__)


class DocumentationQualityMixin:
    """Phase 4: Quality Assessment"""

    repo_root: "Path"
    results: "dict[str, Any]"

    def phase4_quality(self):
        """Phase 4: Quality Assessment"""
        print("=" * 80)
        print("PHASE 4: QUALITY ASSESSMENT")
        print("=" * 80)
        print()

        # 4.1 Clarity and Readability
        print("4.1 Assessing clarity and readability...")
        quality_issues = self._assess_clarity_readability()
        self.results["phase4"]["quality_issues"] = quality_issues
        print(f"  ✓ Found {len(quality_issues)} quality issues")
        print()

        # 4.2 Actionability
        print("4.2 Assessing actionability...")
        actionability_issues = self._assess_actionability()
        self.results["phase4"]["actionability_issues"] = actionability_issues
        print(f"  ✓ Found {len(actionability_issues)} actionability issues")
        print()

        # 4.3 Maintainability
        print("4.3 Assessing maintainability...")
        maintainability_issues = self._assess_maintainability()
        self.results["phase4"]["maintainability_issues"] = maintainability_issues
        print(f"  ✓ Found {len(maintainability_issues)} maintainability issues")
        print()

        print("✓ Phase 4 complete!")
        print()
        return self.results["phase4"]

    def _assess_clarity_readability(self) -> list[dict]:
        """Assess clarity and readability of documentation."""
        issues = []

        # Check for very long lines (potential readability issue)
        all_md_files = list(self.repo_root.rglob("*.md"))
        for md_file in all_md_files[:50]:  # Sample
            try:
                content = md_file.read_text(encoding="utf-8")
                for i, line in enumerate(content.split("\n"), 1):
                    if len(line) > 120:  # Long line threshold
                        issues.append(
                            {
                                "type": "long_line",
                                "file": str(md_file.relative_to(self.repo_root)),
                                "line": i,
                                "length": len(line),
                            }
                        )
            except Exception as e:
                logger.warning("Failed to read markdown file %s: %s", md_file, e)

        return issues[:20]  # Limit results

    def _assess_actionability(self) -> list[dict]:
        """Assess actionability of instructions."""
        issues = []

        # Check for TODO/FIXME markers (incomplete instructions)
        all_md_files = list(self.repo_root.rglob("*.md"))
        for md_file in all_md_files[:100]:  # Sample
            try:
                content = md_file.read_text(encoding="utf-8")
                if "TODO" in content or "FIXME" in content:
                    issues.append(
                        {
                            "type": "incomplete_content",
                            "file": str(md_file.relative_to(self.repo_root)),
                            "marker": "TODO/FIXME",
                        }
                    )
            except Exception as e:
                logger.warning("Failed to read markdown file %s: %s", md_file, e)

        return issues[:20]  # Limit results

    def _assess_maintainability(self) -> list[dict]:
        """Assess maintainability of documentation."""
        issues = []

        # Check for duplicate content patterns
        # This is a simplified check - full duplication detection would be more complex
        return issues
