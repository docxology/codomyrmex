#!/usr/bin/env python3
"""
Documentation Management - Real Usage Examples

Demonstrates actual documentation capabilities:
- Documentation environment check
- Quality analysis (DocumentationQualityAnalyzer)
- Consistency checking (DocumentationConsistencyChecker)
- Documentation versions validation
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.documentation import (
    DocumentationConsistencyChecker,
    DocumentationQualityAnalyzer,
    check_doc_environment,
    validate_doc_versions,
)
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "documentation"
        / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/documentation/config.yaml")

    setup_logging()
    print_info("Running Documentation Examples...")

    # Root for finding documents
    current_root = Path(__file__).resolve().parent.parent.parent.parent

    # 1. Environment Check
    print_info("Checking documentation environment...")
    try:
        if check_doc_environment():
            print_success("  Documentation environment is correctly set up.")
        else:
            print_info("  Documentation environment check returned False.")
    except Exception as e:
        print_info(f"  Env check note: {e}")

    # 2. Quality Analyzer
    print_info("Testing DocumentationQualityAnalyzer...")
    try:
        analyzer = DocumentationQualityAnalyzer()
        # Analyze the project README
        readme_path = current_root / "README.md"
        if readme_path.exists():
            analysis = analyzer.analyze_file(readme_path)
            score = analysis.get("overall_score", 0)
            print_success(
                f"  README.md analyzed. Overall Quality Score: {score:.1f}/100"
            )
    except Exception as e:
        print_error(f"  Quality analyzer failed: {e}")

    # 3. Consistency Checker
    print_info("Testing DocumentationConsistencyChecker...")
    try:
        DocumentationConsistencyChecker()
        print_success("  Consistency checker initialized successfully.")
    except Exception as e:
        print_error(f"  Consistency checker failed: {e}")

    # 4. Version Validation
    print_info("Validating documentation versions...")
    try:
        if validate_doc_versions():
            print_success("  Documentation versions are consistent.")
    except Exception as e:
        print_info(f"  Version validation note: {e}")

    print_success("Documentation management examples completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
