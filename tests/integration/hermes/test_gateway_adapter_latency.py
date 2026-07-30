"""Integration tests for Hermes gateway platform latency metrics."""

import time

from codomyrmex.agents.hermes.gateway.platforms.metrics import PlatformContext


def test_platform_context_latency_metrics() -> None:
    """Ensure platform metrics accurately split IO vs LLM inference time."""
    context = PlatformContext(platform_name="telegram", user_id="123")

    # Simulate gateway routing taking 0.1s
    time.sleep(0.1)

    # Simulate LLM taking 0.4s
    with context.measure_inference():
        time.sleep(0.4)

    # Simulate response formatting taking 0.05s
    time.sleep(0.05)

    context.finalize()

    # Calculate exacts
    metrics = context.metrics.to_dict()

    assert metrics["total_latency_ms"] > 0

    # Sleep establishes a minimum duration; a loaded runner can resume later.
    assert metrics["llm_inference_latency_ms"] >= 390.0

    # Routing plus formatting likewise establishes a minimum of about 150ms.
    assert metrics["platform_io_latency_ms"] >= 140.0
    assert metrics["total_latency_ms"] >= 530.0

    # The split remains the substantive contract: inference is excluded from IO.
    assert (
        abs(
            metrics["total_latency_ms"]
            - (metrics["llm_inference_latency_ms"] + metrics["platform_io_latency_ms"])
        )
        < 1.0
    )
