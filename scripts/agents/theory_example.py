#!/usr/bin/env python3
"""
Theory Module Example - Agent Architectures and Reasoning

Demonstrates usage of theoretical agent components: ReactiveArchitecture,
DeliberativeArchitecture with KnowledgeBase, and SymbolicReasoningModel.
"""
import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.agents import ReactiveArchitecture, DeliberativeArchitecture
from codomyrmex.agents.theory.reasoning_models import SymbolicReasoningModel
from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_section


def main():
    setup_logging()
    print_section("Agent Theory Examples")

    # --- Reactive Architecture ---
    print_info("1. Reactive Architecture Demo")
    reactive = ReactiveArchitecture()

    # Add rules
    reactive.add_rule(
        condition=lambda env: env.get("temperature", 0) > 30,
        action=lambda env: {"action": "cool_down", "temp": env["temperature"]}
    )
    reactive.add_rule(
        condition=lambda env: env.get("temperature", 0) < 10,
        action=lambda env: {"action": "heat_up", "temp": env["temperature"]}
    )

    # Simulate perception -> decision -> action
    environment = {"temperature": 35}
    perception = reactive.perceive(environment)
    decision = reactive.decide(perception)
    result = reactive.act(decision)
    print_success(f"Reactive Result: {result}")

    # --- Deliberative Architecture with KnowledgeBase ---
    print_info("\n2. Deliberative Architecture Demo")
    deliberative = DeliberativeArchitecture()
    
    # Set goals
    deliberative.set_goal({"type": "simple", "target": "optimize_code"})
    
    # Simulate environment with facts
    environment = {"code_quality": 0.7, "test_coverage": 0.5}
    perception = deliberative.perceive(environment)
    decision = deliberative.decide(perception)
    result = deliberative.act(decision)
    print_success(f"Deliberative Result: {result}")
    print_info(f"Knowledge Base Facts: {deliberative.kb.facts}")

    # --- Symbolic Reasoning ---
    print_info("\n3. Symbolic Reasoning Demo")
    reasoner = SymbolicReasoningModel()

    # Add facts and rules
    reasoner.add_fact("is_python", True)
    reasoner.add_fact("has_tests", True)
    reasoner.add_rule({
        "conditions": [
            {"fact": "is_python", "operator": "==", "value": True},
            {"fact": "has_tests", "operator": "==", "value": True},
        ],
        "conclusion": {"quality": "high"}
    })

    # Reason
    result = reasoner.reason(premises={"lines_of_code": 500})
    explanation = reasoner.explain(result)
    print_success(f"Reasoning Result: {result['conclusions']}")
    print_info(f"Explanation: {explanation}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
