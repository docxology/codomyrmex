"""MCP tools for the networking service mesh module."""

import json

from codomyrmex.model_context_protocol.decorators import mcp_tool
from codomyrmex.networking.service_mesh.models import (
    CircuitBreakerConfig,
    LoadBalancerStrategy,
    ServiceInstance,
)
from codomyrmex.networking.service_mesh.resilience import CircuitBreaker, LoadBalancer


@mcp_tool()
def service_mesh_circuit_breaker_simulate(name: str, failures: int) -> str:
    """Simulate a circuit breaker state after a number of failures.

    Args:
        name: Name of the circuit breaker.
        failures: Number of consecutive failures to record.

    Returns:
        JSON string representing the state of the circuit breaker.
    """
    config = CircuitBreakerConfig(failure_threshold=3)
    cb = CircuitBreaker(name, config)

    for _ in range(failures):
        cb.record_failure()

    return json.dumps(
        {"name": cb.name, "state": cb.state.value, "failure_count": cb.failure_count}
    )


@mcp_tool()
def service_mesh_load_balancer_simulate(strategy_name: str, instances: str) -> str:
    """Simulate load balancer strategy by choosing from instances.

    Args:
        strategy_name: Name of the LoadBalancerStrategy (ROUND_ROBIN, RANDOM, WEIGHTED, LEAST_CONNECTIONS).
        instances: JSON string list of objects with id, host, port, weight, and connections.

    Returns:
        JSON string of the selected instance id.
    """
    try:
        strategy = LoadBalancerStrategy[strategy_name.upper()]
    except KeyError:
        return f"Unknown strategy: {strategy_name}"

    lb = LoadBalancer(strategy=strategy)

    try:
        instance_list = json.loads(instances)
    except json.JSONDecodeError as e:
        return f"Error parsing instances: {e}"

    for inst_data in instance_list:
        inst = ServiceInstance(
            id=inst_data.get("id", ""),
            host=inst_data.get("host", "localhost"),
            port=inst_data.get("port", 80),
            weight=inst_data.get("weight", 1),
            connections=inst_data.get("connections", 0),
        )
        lb.register(inst)

    selected = lb.get_instance()

    if selected:
        return json.dumps({"selected_id": selected.id})
    return "No instances available"
