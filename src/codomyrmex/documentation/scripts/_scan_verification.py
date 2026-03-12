"""Phase 6: Verification and Validation for Documentation Scan."""

import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any


class DocumentationVerificationMixin:
    """Phase 6: Verification and Validation"""

    repo_root: "Path"
    results: "dict[str, Any]"

    def phase6_verification(self):
        """Phase 6: Verification and Validation"""
        print("=" * 80)
        print("PHASE 6: VERIFICATION AND VALIDATION")
        print("=" * 80)
        print()

        # 6.1 Automated Checks
        print("6.1 Running automated validation tools...")
        validation_results = self._run_automated_checks()
        self.results["phase6"]["validation_results"] = validation_results
        print("  ✓ Completed automated checks")
        print()

        # 6.2 Manual Review Notes
        print("6.2 Manual review checklist...")
        manual_notes = self._generate_manual_review_checklist()
        self.results["phase6"]["manual_review_notes"] = manual_notes
        print("  ✓ Generated manual review checklist")
        print()

        print("✓ Phase 6 complete!")
        print()
        return self.results["phase6"]

    def _run_automated_checks(self) -> dict:
        """Run existing validation tools."""
        results = {}

        tools_to_run = [
            ("comprehensive_audit", "scripts/documentation/comprehensive_audit.py"),
            ("module_docs_auditor", "scripts/documentation/module_docs_auditor.py"),
            ("check_doc_links", "scripts/documentation/check_doc_links.py"),
        ]

        for tool_name, tool_path in tools_to_run:
            full_path = self.repo_root / tool_path
            if full_path.exists():
                try:
                    result = subprocess.run(
                        ["python3", str(full_path)],
                        cwd=self.repo_root,
                        capture_output=True,
                        text=True,
                        timeout=120,
                    )
                    results[tool_name] = {
                        "exit_code": result.returncode,
                        "stdout": result.stdout[:1000],  # Limit output
                        "stderr": result.stderr[:1000] if result.stderr else "",
                    }
                except Exception as e:
                    results[tool_name] = {"error": str(e)}
            else:
                results[tool_name] = {"error": "Tool not found"}

        return results

    def _generate_manual_review_checklist(self) -> list[str]:
        """Generate checklist for manual review."""
        checklist = [
            "Read through as a new user - follow getting started path",
            "Follow all workflows end-to-end",
            "Test installation process",
            "Verify development setup",
            "Check module creation tutorial",
            "Verify all examples work",
            "Check all cross-references",
            "Validate consistency",
        ]
        return checklist
