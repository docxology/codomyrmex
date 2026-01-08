#!/usr/bin/env python3
"""
CI/CD Dependency Validation Script.

This script validates module dependencies and fails CI if violations are found.
"""

import sys
from pathlib import Path

# Add tools to path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root / "tools"))

# Add current directory to path to find sibling modules
sys.path.insert(0, str(Path(__file__).parent))

try:
    from dependency_analyzer import DependencyAnalyzer
except ImportError:
    # Try importing from src if available (fallback)
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "codomyrmex" / "tools"))
    try:
        from dependency_analyzer import DependencyAnalyzer
    except ImportError:
        print("Error: Could not import DependencyAnalyzer")
        sys.exit(1)

try:
    from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging

    setup_logging()
    logger = get_logger(__name__)
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


def main() -> int:
    """Run dependency validation."""
    repo_root = Path(__file__).parent.parent.parent
    analyzer = DependencyAnalyzer(repo_root)

    logger.info("Running dependency validation...")
    results = analyzer.analyze()

    # Check for issues
    has_issues = False

    if results["circular_dependencies"]:
        logger.error("Circular dependencies detected:")
        for mod1, mod2 in results["circular_dependencies"]:
            logger.error(f"  - {mod1} ↔ {mod2}")
        has_issues = True

    if results["violations"]:
        logger.error("Dependency hierarchy violations detected:")
        for violation in results["violations"]:
            logger.error(
                f"  - {violation['module']} imports {violation['imported']} "
                f"(allowed: {violation['allowed']})"
            )
        has_issues = True

    if has_issues:
        logger.error("❌ Dependency validation failed!")
        return 1

    logger.info("✅ Dependency validation passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

