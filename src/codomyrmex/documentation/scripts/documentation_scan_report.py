"""
Comprehensive Documentation Scan and Improvement Tool

This script implements a 7-phase approach to scan, verify, and improve
all documentation across the Codomyrmex repository.
"""

from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

from ._scan_accuracy import DocumentationAccuracyMixin
from ._scan_completeness import DocumentationCompletenessMixin
from ._scan_discovery import DocumentationDiscoveryMixin
from ._scan_improvements import DocumentationImprovementsMixin
from ._scan_quality import DocumentationQualityMixin
from ._scan_reporting import DocumentationReportingMixin
from ._scan_verification import DocumentationVerificationMixin

logger = get_logger(__name__)


class DocumentationScanner(
    DocumentationDiscoveryMixin,
    DocumentationAccuracyMixin,
    DocumentationCompletenessMixin,
    DocumentationQualityMixin,
    DocumentationImprovementsMixin,
    DocumentationVerificationMixin,
    DocumentationReportingMixin,
):
    """Comprehensive documentation scanner and analyzer."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root.resolve()
        self.results = {
            "phase1": {"files_found": {}, "structure_map": {}, "tools_inventory": {}},
            "phase2": {
                "content_issues": [],
                "reference_issues": [],
                "terminology_issues": [],
            },
            "phase3": {"coverage_gaps": [], "audience_gaps": [], "cross_ref_gaps": []},
            "phase4": {
                "quality_issues": [],
                "actionability_issues": [],
                "maintainability_issues": [],
            },
            "phase5": {"improvements_made": [], "files_updated": []},
            "phase6": {"validation_results": {}, "manual_review_notes": []},
            "phase7": {"summary_stats": {}, "issue_catalog": [], "recommendations": []},
        }


def main():
    """Main execution function."""
    repo_root = Path(__file__).parent.parent.parent.parent.parent
    scanner = DocumentationScanner(repo_root)

    # Execute all phases
    scanner.phase1_discovery()
    scanner.phase2_accuracy()
    scanner.phase3_completeness()
    scanner.phase4_quality()
    scanner.phase5_improvements()
    scanner.phase6_verification()
    scanner.phase7_reporting()

    # Generate report
    report = scanner.generate_report()
    print(report)

    # Save results
    output_dir = repo_root / "@output" / "documentation_scan"
    output_dir.mkdir(parents=True, exist_ok=True)
    scanner.save_results(output_dir / "scan_results.json")
    (output_dir / "scan_report.md").write_text(report)

    print(f"\n✓ Results saved to {output_dir}")


if __name__ == "__main__":
    main()
