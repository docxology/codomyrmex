"""Phase 7: Reporting for Documentation Scan."""

import json
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any


class DocumentationReportingMixin:
    """Phase 7: Reporting"""

    repo_root: "Path"
    results: "dict[str, Any]"

    def phase7_reporting(self):
        """Phase 7: Reporting"""
        print("=" * 80)
        print("PHASE 7: REPORTING")
        print("=" * 80)
        print()

        # 7.1 Summary Statistics
        print("7.1 Generating summary statistics...")
        summary_stats = self._generate_summary_stats()
        self.results["phase7"]["summary_stats"] = summary_stats
        print("  ✓ Generated summary statistics")
        print()

        # 7.2 Issue Catalog
        print("7.2 Compiling issue catalog...")
        issue_catalog = self._compile_issue_catalog()
        self.results["phase7"]["issue_catalog"] = issue_catalog
        print("  ✓ Compiled issue catalog")
        print()

        # 7.3 Recommendations
        print("7.3 Generating recommendations...")
        recommendations = self._generate_recommendations()
        self.results["phase7"]["recommendations"] = recommendations
        print("  ✓ Generated recommendations")
        print()

        print("✓ Phase 7 complete!")
        print()
        return self.results["phase7"]

    def _generate_summary_stats(self) -> dict:
        """Generate summary statistics."""
        stats = {
            "total_files_scanned": self.results["phase1"]["files_found"].get(
                "total_markdown", 0
            ),
            "issues_by_category": {
                "broken_links": len(self.results["phase2"]["reference_issues"]),
                "missing_documentation": len(self.results["phase3"]["coverage_gaps"]),
                "outdated_information": len(self.results["phase2"]["content_issues"]),
                "inconsistencies": len(self.results["phase2"]["terminology_issues"]),
                "quality_issues": len(self.results["phase4"]["quality_issues"]),
            },
            "improvements_identified": len(self.results["phase5"]["improvements_made"]),
            "links_verified": len(self.results["phase2"]["reference_issues"]),
        }
        return stats

    def _compile_issue_catalog(self) -> list[dict]:
        """Compile comprehensive issue catalog."""
        catalog = []

        # Add issues from all phases
        catalog.extend(self.results["phase2"]["content_issues"])
        catalog.extend(self.results["phase2"]["reference_issues"])
        catalog.extend(self.results["phase2"]["terminology_issues"])
        catalog.extend(self.results["phase3"]["coverage_gaps"])
        catalog.extend(self.results["phase3"]["audience_gaps"])
        catalog.extend(self.results["phase4"]["quality_issues"])

        return catalog

    def _generate_recommendations(self) -> list[dict]:
        """Generate recommendations for improvements."""
        recommendations = []

        if self.results["phase2"]["reference_issues"]:
            recommendations.append(
                {
                    "area": "Link Validation",
                    "priority": "critical",
                    "recommendation": "Fix all broken internal links identified in Phase 2",
                    "count": len(self.results["phase2"]["reference_issues"]),
                }
            )

        if self.results["phase3"]["coverage_gaps"]:
            recommendations.append(
                {
                    "area": "Documentation Coverage",
                    "priority": "high",
                    "recommendation": "Add missing documentation files identified in Phase 3",
                    "count": len(self.results["phase3"]["coverage_gaps"]),
                }
            )

        recommendations.append(
            {
                "area": "Process Improvement",
                "priority": "medium",
                "recommendation": "Set up automated documentation validation in CI/CD pipeline",
                "count": 0,
            }
        )

        return recommendations

    def generate_report(self) -> str:
        """Generate comprehensive report."""
        report = []
        report.append("# Documentation Scan and Improvement Report")
        report.append(f"\nGenerated: {datetime.now().isoformat()}")
        report.append(f"\nRepository: {self.repo_root}")
        report.append("\n" + "=" * 80 + "\n")

        # Phase 1 Summary
        if self.results["phase1"]["files_found"]:
            p1 = self.results["phase1"]
            report.append("## Phase 1: Discovery and Inventory")
            report.append(
                f"\n- Total Markdown Files: {p1['files_found'].get('total_markdown', 0)}"
            )
            report.append(
                f"- AGENTS.md Files: {p1['files_found'].get('agents_files', 0)}"
            )
            report.append(
                f"- README.md Files: {p1['files_found'].get('readme_files', 0)}"
            )
            report.append(
                f"- Configuration Files: {len(p1['files_found'].get('config_files', []))}"
            )
            report.append(
                f"- Documentation Categories: {len(p1['structure_map'].get('categories', {}))}"
            )
            report.append(
                f"- Validation Tools Found: {len(p1['tools_inventory'].get('existing_tools', []))}"
            )
            report.append("\n")

        # Phase 2 Summary
        p2 = self.results["phase2"]
        report.append("## Phase 2: Accuracy Verification")
        report.append(f"\n- Content Issues: {len(p2['content_issues'])}")
        report.append(f"- Reference Issues: {len(p2['reference_issues'])}")
        report.append(f"- Terminology Issues: {len(p2['terminology_issues'])}")
        report.append("\n")

        # Phase 3 Summary
        p3 = self.results["phase3"]
        report.append("## Phase 3: Completeness Analysis")
        report.append(f"\n- Coverage Gaps: {len(p3['coverage_gaps'])}")
        report.append(f"- Audience Gaps: {len(p3['audience_gaps'])}")
        report.append(f"- Cross-Reference Gaps: {len(p3['cross_ref_gaps'])}")
        report.append("\n")

        # Phase 4 Summary
        p4 = self.results["phase4"]
        report.append("## Phase 4: Quality Assessment")
        report.append(f"\n- Quality Issues: {len(p4['quality_issues'])}")
        report.append(f"- Actionability Issues: {len(p4['actionability_issues'])}")
        report.append(f"- Maintainability Issues: {len(p4['maintainability_issues'])}")
        report.append("\n")

        # Phase 5 Summary
        p5 = self.results["phase5"]
        report.append("## Phase 5: Intelligent Improvements")
        report.append(f"\n- Improvements Identified: {len(p5['improvements_made'])}")
        report.append(f"- Files Updated: {len(p5.get('files_updated', []))}")
        report.append("\n")

        # Phase 6 Summary
        p6 = self.results["phase6"]
        report.append("## Phase 6: Verification and Validation")
        report.append(
            f"\n- Validation Tools Run: {len(p6.get('validation_results', {}))}"
        )
        report.append(
            f"- Manual Review Items: {len(p6.get('manual_review_notes', []))}"
        )
        report.append("\n")

        # Phase 7 Summary
        p7 = self.results["phase7"]
        if p7.get("summary_stats"):
            stats = p7["summary_stats"]
            report.append("## Phase 7: Reporting")
            report.append("\n### Summary Statistics")
            report.append(
                f"\n- Total Files Scanned: {stats.get('total_files_scanned', 0)}"
            )
            report.append("- Issues by Category:")
            for category, count in stats.get("issues_by_category", {}).items():
                report.append(f"  - {category}: {count}")
            report.append(
                f"- Improvements Identified: {stats.get('improvements_identified', 0)}"
            )
            report.append("\n### Recommendations")
            for rec in p7.get("recommendations", []):
                report.append(
                    f"\n- **{rec['area']}** ({rec['priority']}): {rec['recommendation']}"
                )
                if rec.get("count", 0) > 0:
                    report.append(f"  - Affects {rec['count']} items")
            report.append("\n")

        return "\n".join(report)

    def save_results(self, output_path: "Path"):
        """Save results to JSON file."""
        output_path.write_text(json.dumps(self.results, indent=2, default=str))
