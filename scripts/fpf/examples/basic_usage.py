#!/usr/bin/env python3
"""
First Principles Framework (FPF) - Real Usage Examples

Demonstrates actual FPF capabilities:
- FPFClient initialization
- Loading/Parsing FPF specification (stubs)
- FPF models (Concept, Pattern, Relationship)
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.fpf import (
    Concept,
    ConceptType,
    FPFClient,
    FPFSpec,
    Pattern,
    PatternStatus,
    Relationship,
    RelationshipType,
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
        Path(__file__).resolve().parent.parent.parent / "config" / "fpf" / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/fpf/config.yaml")

    setup_logging()
    print_info("Running FPF Examples...")

    # 1. FPFClient
    print_info("Testing FPFClient initialization...")
    try:
        FPFClient()
        print_success("  FPFClient initialized successfully.")
    except Exception as e:
        print_error(f"  FPFClient failed: {e}")

    # 2. Models
    print_info("Testing FPF models...")
    try:
        spec = FPFSpec(version="1.0.0")
        print_success(f"  FPFSpec instance created: {spec.version}")

        concept = Concept(
            name="Test Concept",
            definition="A concept used by the example.",
            pattern_id="pattern1",
            type=ConceptType.TERM,
        )
        print_success(f"  Concept model instance created: {concept.name}")

        pattern = Pattern(
            id="pattern1",
            title="Test Pattern",
            status=PatternStatus.DRAFT,
            content="A demonstration pattern.",
        )
        print_success(f"  Pattern model instance created: {pattern.title}")

        Relationship(
            source="concept1",
            target="pattern1",
            type=RelationshipType.USED_BY,
        )
        print_success("  Relationship model instance created.")
    except Exception as e:
        print_error(f"  Models check failed: {e}")

    print_success("FPF examples completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
