#!/usr/bin/env python3
"""
Orchestrator for documentation.
Utilizes the documentation module's API to perform a full audit and quality report generation.
"""

import sys
from pathlib import Path
from datetime import datetime

# Ensure codomyrmex is in path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root / "src") not in sys.path:
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.documentation import (
    audit_documentation,
    generate_quality_report,
    DocumentationConsistencyChecker,
    check_doc_environment
)
from codomyrmex.utils.cli_helpers import (
    print_section,
    print_info,
    print_success,
    print_warning,
    print_error
)

def run_orchestration():
    print_section("Documentation Orchestrator")
    
    # 1. Check environment
    print_info("Step 1: Checking environment...")
    if not check_doc_environment():
        print_warning("Environment check failed or partially failed (Node.js/npm missing). Website features may not work.")
    else:
        print_success("Environment check passed.")

    # 2. Audit Documentation (RASP compliance)
    print_info("\nStep 2: Auditing documentation compliance (RASP)...")
    src_dir = project_root / "src" / "codomyrmex"
    report_dir = project_root / "output" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    audit_report_file = report_dir / f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    try:
        audit_documentation(src_dir, audit_report_file)
        print_success(f"Audit report generated at: {audit_report_file}")
    except Exception as e:
        print_error(f"Audit failed: {e}")

    # 3. Check Consistency
    print_info("\nStep 3: Checking documentation consistency...")
    checker = DocumentationConsistencyChecker()
    # Check the documentation module itself as an example
    doc_module_path = src_dir / "documentation"
    consistency_report = checker.check_directory(str(doc_module_path))
    
    if consistency_report.passed:
        print_success(f"Consistency check passed for {doc_module_path}")
    else:
        print_warning(f"Consistency check found {len(consistency_report.issues)} issues in {doc_module_path}")
        for issue in consistency_report.issues[:5]: # Show first 5
            print(f"  [{issue.severity}] {issue.file_path}:{issue.line_number} - {issue.description}")
        if len(consistency_report.issues) > 5:
            print(f"  ... and {len(consistency_report.issues) - 5} more issues.")

    # 4. Generate Quality Report
    print_info("\nStep 4: Generating quality report...")
    try:
        quality_report = generate_quality_report(project_root)
        quality_report_file = report_dir / f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        quality_report_file.write_text(quality_report, encoding="utf-8")
        print_success(f"Quality report generated at: {quality_report_file}")
    except Exception as e:
        print_error(f"Quality report generation failed: {e}")

    print_section("Orchestration Complete")

if __name__ == "__main__":
    run_orchestration()
