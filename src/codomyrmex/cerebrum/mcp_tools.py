from typing import Any

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool

logger = get_logger(__name__)


@mcp_tool(category="cerebrum")
def query_knowledge_base(query: str, limit: int = 5) -> dict:
    """Perform semantic retrieval from the CaseBase.

    Args:
        query: The semantic concept or question to search for
        limit: Maximum number of cases to return

    Returns:
        Structured retrieval results containing matching cases.
    """
    if not query or not query.strip():
        return {"status": "error", "message": "query must be a non-empty string"}
    if not isinstance(limit, int) or limit < 1 or limit > 100:
        return {"status": "error", "message": "limit must be an integer between 1 and 100"}

    from codomyrmex.cerebrum import CaseBase, CaseRetriever

    base = CaseBase()
    retriever = CaseRetriever(base)
    results = retriever.retrieve({"concept": query}, k=limit)

    formatted_results = [
        {
            "id": case.case_id,
            "features": case.features,
            "solution": case.metadata.get("solution"),
            "similarity_score": score,
        }
        for case, score in results
    ]
    return {
        "status": "success",
        "results": formatted_results,
        "count": len(formatted_results),
    }


@mcp_tool(category="cerebrum")
def add_case_reference(concept: str, solution: str) -> dict:
    """Store intelligence context directly into the CaseBase.

    Args:
        concept: The problem or concept feature string
        solution: The paired resolution or insight

    Returns:
        Confirmation of case storage.
    """
    if not concept or not concept.strip():
        return {"status": "error", "message": "concept must be a non-empty string"}
    if not solution or not solution.strip():
        return {"status": "error", "message": "solution must be a non-empty string"}

    import uuid

    from codomyrmex.cerebrum import Case, CaseBase

    base = CaseBase()
    case_id = str(uuid.uuid4())
    case = Case(case_id=case_id, features={"concept": concept}, metadata={"solution": solution})
    base.add_case(case)

    return {
        "status": "success",
        "message": "Case stored successfully",
        "case_id": case.case_id,
    }
@mcp_tool(
    category="cerebrum",
    description="Evaluate prediction-error 'surprise' (Free Energy) to trigger swarm deployment.",
)
def evaluate_surprise_signal(observation: dict[str, Any], threshold: float = 5.0) -> dict[str, Any]:
    """Evaluate surprise signal using active inference.

    If free energy > threshold, recommend swarm deployment.

    Args:
        observation: Data features to evaluate (e.g. {'anomaly_score': 0.8, 'drift': 0.5})
        threshold: Surprise threshold (default 5.0)
    """
    from codomyrmex.cerebrum.inference.active_inference import (
        BeliefState,
        VariationalFreeEnergy,
    )

    # Define a default 2-state model
    # States: nominal, critical
    states = {"nominal": 0.9, "critical": 0.1}
    beliefs = BeliefState(states=states)

    # Likelihood model: How likely are these observations in each state?
    # In 'nominal', seeing an 'anomaly' observation should have low probability.
    # In 'critical', seeing it should have high probability.
    likelihood = {
        "nominal": dict.fromkeys(observation, 0.1),
        "critical": dict.fromkeys(observation, 0.9),
    }

    vfe = VariationalFreeEnergy(precision=1.0)
    fe = vfe.compute(beliefs, observation, likelihood)

    should_deploy = fe > threshold

    return {
        "status": "success",
        "free_energy": fe,
        "threshold": threshold,
        "recommendation": "DEPLOY_SWARM" if should_deploy else "MONITOR",
        "signal_strength": round(max(0.0, fe / threshold), 2) if threshold > 0 else 0.0,
        "observation_keys": list(observation.keys()),
    }


@mcp_tool(
    category="cerebrum",
    description="Run a free-energy minimization loop with an active inference agent.",
)
def cerebrum_run_free_energy_loop(
    observation: dict[str, Any],
    max_steps: int = 50,
    threshold: float = 0.1,
    convergence_window: int = 3,
) -> dict[str, Any]:
    """Run a closed-loop free-energy minimization using active inference.

    Creates a default 2-state agent and iterates until variational free
    energy converges below the threshold or the step limit is reached.

    Args:
        observation: Initial observation dict (e.g. {"sensor": 0.5}).
        max_steps: Maximum perception-action cycles (default 50).
        threshold: Free energy convergence threshold (default 0.1).
        convergence_window: Consecutive steps below threshold needed (default 3).

    Returns:
        dict with keys: status, converged, steps, final_free_energy, action_history
    """
    try:
        from codomyrmex.cerebrum.inference.active_inference import (
            ActiveInferenceAgent,
            BeliefState,
            GenerativeModel,
        )
        from codomyrmex.cerebrum.inference.free_energy_loop import FreeEnergyLoop

        # Build a default 2-state generative model
        states = {"nominal": 0.5, "anomalous": 0.5}
        beliefs = BeliefState(states=states)
        transitions = {
            "stay": {"nominal": {"nominal": 0.9, "anomalous": 0.1},
                     "anomalous": {"nominal": 0.1, "anomalous": 0.9}},
            "switch": {"nominal": {"nominal": 0.3, "anomalous": 0.7},
                       "anomalous": {"nominal": 0.7, "anomalous": 0.3}},
        }
        likelihood = {
            "nominal": dict.fromkeys(observation, 0.8),
            "anomalous": dict.fromkeys(observation, 0.2),
        }
        model = GenerativeModel(
            transitions=transitions,
            likelihood=likelihood,
            preferences={"nominal": 0.8, "anomalous": 0.2},
        )
        agent = ActiveInferenceAgent(beliefs=beliefs, model=model)
        loop = FreeEnergyLoop(
            agent=agent,
            max_steps=max_steps,
            fe_threshold=threshold,
            convergence_window=convergence_window,
        )
        result = loop.run(observation)
        return {
            "status": "success",
            "converged": result.converged,
            "steps": result.steps,
            "final_free_energy": result.final_free_energy,
            "action_history": result.action_history,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
