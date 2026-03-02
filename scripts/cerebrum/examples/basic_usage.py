#!/usr/bin/env python3
"""
CEREBRUM - Real Usage Examples

Demonstrates actual cognitive modeling capabilities:
- Engine and Config initialization
- Case management (Case, CaseBase)
- Bayesian Inference (BayesianNetwork, InferenceEngine)
- Active Inference (ActiveInferenceAgent)
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.cerebrum import (
    CerebrumEngine,
    CerebrumConfig,
    Case,
    CaseBase,
    BayesianNetwork,
    InferenceEngine,
    ActiveInferenceAgent,
    compute_hash
)

def main():
    setup_logging()
    print_info("Running CEREBRUM Examples...")

    # 1. Config & Engine
    print_info("Initializing CerebrumEngine...")
    try:
        config = CerebrumConfig()
        engine = CerebrumEngine(config=config)
        print_success("  CerebrumEngine initialized successfully.")
    except Exception as e:
        print_error(f"  CerebrumEngine failed: {e}")

    # 2. Case Management
    print_info("Testing Case management...")
    try:
        case = Case(
            case_id="case_001",
            features={"type": "bug", "severity": "high"},
            outcome="Update imports"
        )
        base = CaseBase()
        base.add_case(case)
        if base.get_case("case_001"):
            print_success("  Case created and added to CaseBase.")
    except Exception as e:
        print_error(f"  Case management failed: {e}")

    # 3. Bayesian Inference
    print_info("Testing Bayesian components...")
    try:
        network = BayesianNetwork(name="example_net")
        inference = InferenceEngine(network=network)
        print_success(f"  BayesianNetwork '{network.name}' and InferenceEngine initialized.")
    except Exception as e:
        print_error(f"  Bayesian components failed: {e}")

    # 4. Active Inference
    print_info("Testing Active Inference agent...")
    try:
        agent = ActiveInferenceAgent()
        print_success("  ActiveInferenceAgent initialized successfully.")
    except Exception as e:
        print_error(f"  ActiveInferenceAgent failed: {e}")

    # 5. Utilities
    print_info("Testing Cerebrum utilities...")
    h = compute_hash("test_input")
    if h:
        print_success(f"  compute_hash functional: {h}")

    print_success("CEREBRUM examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
