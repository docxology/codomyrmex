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

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.fpf import (
    FPFClient,
    FPFSpec,
    Concept,
    Pattern,
    Relationship
)

def main():
    setup_logging()
    print_info("Running FPF Examples...")

    # 1. FPFClient
    print_info("Testing FPFClient initialization...")
    try:
        client = FPFClient()
        print_success("  FPFClient initialized successfully.")
    except Exception as e:
        print_error(f"  FPFClient failed: {e}")

    # 2. Models
    print_info("Testing FPF models...")
    try:
        spec = FPFSpec(title="Demo Spec", version="1.0.0")
        print_success(f"  FPFSpec instance created: {spec.title}")
        
        concept = Concept(id="concept1", name="Test Concept")
        print_success(f"  Concept model instance created: {concept.name}")
        
        pattern = Pattern(id="pattern1", name="Test Pattern")
        print_success(f"  Pattern model instance created: {pattern.name}")
        
        rel = Relationship(id="rel1", source_id="concept1", target_id="pattern1")
        print_success(f"  Relationship model instance created.")
    except Exception as e:
        print_error(f"  Models check failed: {e}")

    print_success("FPF examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
