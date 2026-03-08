#!/usr/bin/env python3
"""Theory — Thin Script Orchestrator.

Instantiates agent architecture patterns: Reactive, Deliberative, Hybrid.

Usage:
    python scripts/agents/theory/run_theory.py
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "src"))

from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def main() -> int:
    setup_logging()
    print_info("Theory — agent architecture patterns...")

    try:
        from codomyrmex.agents.theory import (
            DeliberativeArchitecture,
            HybridArchitecture,
            NeuralReasoningModel,
            ReactiveArchitecture,
            ReasoningModel,
            SymbolicReasoningModel,
        )
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1

    print_success("Architecture patterns imported:")
    for arch in [ReactiveArchitecture, DeliberativeArchitecture, HybridArchitecture]:
        print_info(f"  {arch.__name__}: {arch.__doc__[:80] if arch.__doc__ else 'no doc'}...")

    print_info("Reasoning models:")
    for model in [SymbolicReasoningModel, NeuralReasoningModel]:
        print_info(f"  {model.__name__}")

    print_success("Theory probe complete.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
