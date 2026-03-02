# Eval Harness -- Agent Integration Guide

## Module Purpose

Provides standardized LLM evaluation tools for agents that need to benchmark model performance, compare metrics, or validate model outputs.

## MCP Tools

| Tool | Description | Inputs | Output |
|------|-------------|--------|--------|
| `eval_harness_run` | Run evaluation tasks against a model | `tasks, metric` | `{num_tasks, mean_score, results}` |
| `eval_harness_score` | Score predictions against targets | `predictions, targets, metric` | `{score, metric, num_examples}` |

## Agent Use Cases

### Model Benchmarking
An agent can use `eval_harness_run` to evaluate model performance on standard QA or classification tasks.

### Quick Scoring
Use `eval_harness_score` for ad-hoc comparison of predictions against gold labels without defining full tasks.

### Regression Detection
Compare scores across model versions to detect regressions.

## Example Agent Workflow

```
1. Agent receives: "Evaluate my model on the QA benchmark"
2. Agent calls: eval_harness_run(tasks=[{name: "qa", examples: [...]}], metric="f1")
3. Response: {"mean_score": 0.78, "results": [...]}
4. Agent reports: "Model achieves 78% F1 on the QA benchmark"
```
