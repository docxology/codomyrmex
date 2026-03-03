#!/usr/bin/env python3
"""
Comprehensive orchestrator for CEREBRUM.
Demonstrates a complete cognitive workflow including CBR, Bayesian Inference, and reasoning chains.
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.cerebrum import (
    ActiveInferenceAgent,
    BayesianNetwork,
    Case,
    CerebrumConfig,
    CerebrumEngine,
    InferenceEngine,
)
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def setup_demo_environment(engine: CerebrumEngine):
    """Setup a demo environment with some initial cases and a Bayesian network."""
    print_info("Setting up demo environment...")

    # 1. Add some initial cases (Bug fixing domain)
    cases = [
        Case(case_id="bug_001", features={"type": "null_pointer", "severity": 5}, outcome="Check for null before access"),
        Case(case_id="bug_002", features={"type": "syntax_error", "severity": 2}, outcome="Fix typo in variable name"),
        Case(case_id="bug_003", features={"type": "performance", "severity": 4}, outcome="Optimize loop complexity"),
        Case(case_id="bug_004", features={"type": "null_pointer", "severity": 3}, outcome="Add default value"),
    ]
    for case in cases:
        engine.add_case(case)

    # 2. Setup a Bayesian Network for bug diagnostics
    # Root nodes: BugType, CodeQuality
    # Child node: FixDifficulty (depends on BugType and CodeQuality)
    network = BayesianNetwork(name="bug_diagnostics")

    # BugType: NullPointer, Syntax, Performance
    network.add_node("BugType", ["NullPointer", "Syntax", "Performance"], [0.4, 0.4, 0.2])
    # CodeQuality: High, Low
    network.add_node("CodeQuality", ["High", "Low"], [0.6, 0.4])

    # FixDifficulty: Easy, Hard
    network.add_node("FixDifficulty", ["Easy", "Hard"])
    network.add_edge("BugType", "FixDifficulty")
    network.add_edge("CodeQuality", "FixDifficulty")

    # Set CPT for FixDifficulty
    # P(FixDifficulty | BugType, CodeQuality)
    cpt = {
        ("NullPointer", "High"): {"Easy": 0.8, "Hard": 0.2},
        ("NullPointer", "Low"): {"Easy": 0.4, "Hard": 0.6},
        ("Syntax", "High"): {"Easy": 0.9, "Hard": 0.1},
        ("Syntax", "Low"): {"Easy": 0.7, "Hard": 0.3},
        ("Performance", "High"): {"Easy": 0.3, "Hard": 0.7},
        ("Performance", "Low"): {"Easy": 0.1, "Hard": 0.9},
    }
    network.set_cpt("FixDifficulty", cpt)

    engine.set_bayesian_network(network)
    print_success("Demo environment setup complete.")

def run_workflow(engine: CerebrumEngine):
    """Run a complete cognitive workflow."""
    print_info("Starting cognitive workflow...")

    # 1. Define a query (A new bug to solve)
    query_case = Case(case_id="new_bug", features={"type": "null_pointer", "severity": 4})
    print_info(f"Query: {query_case.features}")

    # 2. Use Reasoning Chain for step-by-step process
    chain = engine.create_reasoning_chain()

    # Step 1: Retrieve similar cases
    def step_retrieve(memory):
        result = engine.reason(query_case)
        memory.store("reasoning_result", result)
        return f"Found {len(result.retrieved_cases)} similar cases"

    chain.add_step("Retrieve similar cases", step_retrieve)

    # Step 2: Diagnostic inference
    def step_diagnose(memory):
        # We know it's a null_pointer, but let's assume CodeQuality is unknown
        # and we want to infer FixDifficulty
        inf_engine = InferenceEngine(engine.bayesian_network)
        evidence = {"BugType": "NullPointer"}
        posterior = inf_engine.infer({"FixDifficulty": None}, evidence)
        memory.store("diagnostic_posterior", posterior)
        return f"Posterior for FixDifficulty: {posterior['FixDifficulty'].probabilities}"

    chain.add_step("Perform diagnostic inference", step_diagnose)

    # Step 3: Active Inference for policy selection
    def step_active_inf(memory):
        # Setup agent if not exists
        if not engine.active_inference_agent:
            agent = ActiveInferenceAgent(
                states=["Safe", "Risky"],
                observations=["Success", "Failure"],
                actions=["Fix", "Ignore"]
            )
            # Simple models
            agent.set_transition_model({
                "Safe_Fix": {"Safe": 0.9, "Risky": 0.1},
                "Risky_Fix": {"Safe": 0.6, "Risky": 0.4},
            })
            agent.set_observation_model({
                "Safe": {"Success": 0.9, "Failure": 0.1},
                "Risky": {"Success": 0.3, "Failure": 0.7},
            })
            engine.set_active_inference_agent(agent)

        action = engine.active_inference_agent.select_action()
        memory.store("agent_action", action)
        return f"Active Inference Agent selected action: {action}"

    chain.add_step("Select action via Active Inference", step_active_inf)

    # Step 4: Make final decision
    def step_decide(memory):
        options = ["Quick fix", "Comprehensive refactor", "Decline"]
        criteria = {"Reliability": 0.8, "Speed": 0.2}

        # Pull data from previous steps
        reasoning_result = memory.retrieve("reasoning_result")
        agent_action = memory.retrieve("agent_action")

        # Mock some scores for the DecisionModule to evaluate
        decision_context = {
            "scores": {
                "Quick fix": {"Reliability": 0.6, "Speed": 0.9},
                "Comprehensive refactor": {"Reliability": 0.95, "Speed": 0.3},
                "Decline": {"Reliability": 0.5, "Speed": 1.0}
            },
            "confidence": reasoning_result.confidence,
            "agent_hint": agent_action
        }

        decision = engine.decide(options, criteria, decision_context)
        memory.store("final_decision", decision)
        return f"Decision: {decision.choice} (Rationale: {decision.rationale})"

    chain.add_step("Make final decision", step_decide)

    # Execute chain
    execution_result = chain.execute(engine.working_memory)

    if execution_result.success:
        print_success("Reasoning chain executed successfully.")
        for i, step in enumerate(execution_result.steps):
            print(f"  [{i+1}] {step.description}: {step.result}")
    else:
        print_error("Reasoning chain failed.")

    final_decision = engine.working_memory.retrieve("final_decision")
    print_success(f"FINAL WORKFLOW OUTPUT: {final_decision.choice if final_decision else 'None'}")

def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "cerebrum" / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print(f"Loaded config from {config_path.name}")

    setup_logging()
    print_info("CEREBRUM Comprehensive Orchestrator starting...")

    try:
        config = CerebrumConfig()
        engine = CerebrumEngine(config=config)

        setup_demo_environment(engine)
        run_workflow(engine)

        print_success("CEREBRUM orchestration demo completed.")
        return 0
    except Exception as e:
        print_error(f"Orchestration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
