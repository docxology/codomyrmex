"""Phase 3: Completeness Analysis for Documentation Scan."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any


class DocumentationCompletenessMixin:
    """Phase 3: Completeness Analysis"""

    repo_root: "Path"
    results: "dict[str, Any]"

    def phase3_completeness(self):
        """Phase 3: Completeness Analysis"""
        print("=" * 80)
        print("PHASE 3: COMPLETENESS ANALYSIS")
        print("=" * 80)
        print()

        # 3.1 Coverage Completeness
        print("3.1 Checking coverage completeness...")
        coverage_gaps = self._check_coverage_completeness()
        self.results["phase3"]["coverage_gaps"] = coverage_gaps
        print(f"  ✓ Found {len(coverage_gaps)} coverage gaps")
        print()

        # 3.2 Audience Completeness
        print("3.2 Checking audience completeness...")
        audience_gaps = self._check_audience_completeness()
        self.results["phase3"]["audience_gaps"] = audience_gaps
        print(f"  ✓ Found {len(audience_gaps)} audience gaps")
        print()

        # 3.3 Cross-Reference Completeness
        print("3.3 Checking cross-reference completeness...")
        cross_ref_gaps = self._check_cross_ref_completeness()
        self.results["phase3"]["cross_ref_gaps"] = cross_ref_gaps
        print(f"  ✓ Found {len(cross_ref_gaps)} cross-reference gaps")
        print()

        print("✓ Phase 3 complete!")
        print()
        return self.results["phase3"]

    def _check_coverage_completeness(self) -> list[dict]:
        """Check if all major features are documented."""
        gaps = []

        # Check module documentation completeness
        modules_dir = self.repo_root / "src" / "codomyrmex"
        if modules_dir.exists():
            for module_dir in modules_dir.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith("_"):
                    readme = module_dir / "README.md"
                    if not readme.exists():
                        gaps.append(
                            {
                                "type": "missing_module_readme",
                                "module": module_dir.name,
                                "path": str(module_dir.relative_to(self.repo_root)),
                            }
                        )

        return gaps

    def _check_audience_completeness(self) -> list[dict]:
        """Check if documentation covers all audience needs."""
        gaps = []

        # Check getting started path
        getting_started = self.repo_root / "docs" / "getting-started"
        required_files = ["installation.md", "quickstart.md"]
        for req_file in required_files:
            if not (getting_started / req_file).exists():
                gaps.append(
                    {
                        "type": "missing_getting_started",
                        "file": req_file,
                        "path": str(getting_started.relative_to(self.repo_root)),
                    }
                )

        return gaps

    def _check_cross_ref_completeness(self) -> list[dict]:
        """Check cross-reference completeness."""
        gaps = []

        # Sample check: verify main README links to key sections
        readme = self.repo_root / "README.md"
        if readme.exists():
            content = readme.read_text(encoding="utf-8")
            key_links = ["docs/README.md", "docs/getting-started", "docs/reference"]
            for link in key_links:
                if link not in content:
                    gaps.append(
                        {
                            "type": "missing_cross_ref",
                            "file": "README.md",
                            "missing_link": link,
                        }
                    )

        return gaps
