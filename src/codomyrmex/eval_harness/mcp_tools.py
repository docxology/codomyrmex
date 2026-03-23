"""MCP tools for the LLM Eval Harness module."""

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="eval_harness")
def eval_harness_run(
    tasks: list[dict] | None = None,
    metric: str = "exact_match",
) -> dict:
    """Run evaluation tasks against an identity model and return metrics.

    Args:
        tasks: list of task dicts, each with 'name' and 'examples' (list of
               {'input': str, 'target': str}). Default provides simple QA tasks.
        metric: Metric to use ('exact_match' or 'f1')

    Returns:
        dict with: num_tasks, mean_score, results per task
    """
    from .harness import EvalHarness, EvalTask

    if tasks is None:
        tasks = [
            {
                "name": "identity_test",
                "examples": [
                    {"input": "hello", "target": "hello"},
                    {"input": "world", "target": "world"},
                    {"input": "foo", "target": "foo"},
                ],
            },
            {
                "name": "case_test",
                "examples": [
                    {"input": "Hello", "target": "hello"},
                    {"input": "WORLD", "target": "world"},
                ],
            },
        ]

    harness = EvalHarness()  # identity model
    eval_tasks = [
        EvalTask(
            name=t["name"],
            examples=t["examples"],
            metric=t.get("metric", metric),
        )
        for t in tasks
    ]

    result = harness.evaluate_all(eval_tasks)
    result["status"] = "success"
    return result


@mcp_tool(category="eval_harness")
def eval_harness_score(
    predictions: list[str] | None = None,
    targets: list[str] | None = None,
    metric: str = "exact_match",
) -> dict:
    """Score predictions against targets using the specified metric.

    Args:
        predictions: list of predicted strings
        targets: list of target/gold strings
        metric: 'exact_match' or 'f1'

    Returns:
        dict with: score, metric, num_examples
    """
    from .harness import ExactMatchMetric, F1Metric

    if predictions is None:
        predictions = ["hello world", "foo bar"]
    if targets is None:
        targets = ["hello world", "foo baz"]

    if metric == "f1":
        score = F1Metric.score(predictions, targets)
    else:
        score = ExactMatchMetric.score(predictions, targets)

    return {
        "score": score,
        "metric": metric,
        "num_examples": len(targets),
        "status": "success",
    }
