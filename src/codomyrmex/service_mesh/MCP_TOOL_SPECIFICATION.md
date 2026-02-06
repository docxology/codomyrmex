# Service Mesh - MCP Tool Specification

This document defines the Model Context Protocol tools for the Service Mesh module, covering service health monitoring, circuit breaker inspection, and load balancer configuration.

## General Considerations

- **Tool Integration**: Provides observability and control over microservice communication patterns.
- **Thread Safety**: All underlying operations are thread-safe.
- **State**: Circuit breaker and load balancer state is held in-memory per process.

---

## Tool: `service_mesh_status`

### 1. Tool Purpose and Description

Returns the overall health status of the service mesh, including all registered services, their circuit breaker states, and load balancer instance counts.

### 2. Invocation Name

`service_mesh_status`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `service_name` | `string` | No | Filter to a specific service (default: all) | `"payment-service"` |
| `include_instances` | `boolean` | No | Include individual instance details (default: false) | `true` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `services` | `array[object]` | List of service statuses | See example below |
| `total_services` | `integer` | Number of registered services | `5` |
| `total_instances` | `integer` | Total service instances across all services | `12` |
| `healthy_instances` | `integer` | Number of healthy instances | `10` |

### 5. Error Handling

- **Service Not Found**: Returns empty `services` array if filtered name does not exist.

### 6. Idempotency

- **Idempotent**: Yes. Read-only status query.

### 7. Usage Examples

```json
{
  "tool_name": "service_mesh_status",
  "arguments": {
    "service_name": "payment-service",
    "include_instances": true
  }
}
```

### 8. Security Considerations

- Read-only operation. No state modification.
- Instance addresses (host:port) may reveal internal network topology; restrict access accordingly.

---

## Tool: `circuit_breaker_status`

### 1. Tool Purpose and Description

Retrieves the current state of circuit breakers, including state (CLOSED/OPEN/HALF_OPEN), failure counts, and configuration thresholds.

### 2. Invocation Name

`circuit_breaker_status`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `breaker_name` | `string` | No | Specific circuit breaker name (default: all) | `"orders"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `breakers` | `array[object]` | List of breaker statuses | See below |
| `total` | `integer` | Number of circuit breakers | `3` |

Each breaker object:

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `name` | `string` | Breaker name | `"orders"` |
| `state` | `string` | Current state | `"closed"` |
| `failure_count` | `integer` | Current failure count | `2` |
| `failure_threshold` | `integer` | Configured threshold | `5` |
| `last_failure_time` | `string\|null` | ISO timestamp of last failure | `"2026-02-05T10:30:00Z"` |

### 5. Error Handling

- **Not Found**: Returns empty `breakers` array if name does not match.

### 6. Idempotency

- **Idempotent**: Yes.

### 7. Usage Examples

```json
{
  "tool_name": "circuit_breaker_status",
  "arguments": {
    "breaker_name": "orders"
  }
}
```

### 8. Security Considerations

- Read-only. Failure counts may indicate ongoing incidents; consider access control.

---

## Tool: `load_balancer_config`

### 1. Tool Purpose and Description

Configures or retrieves load balancer settings for a service, including strategy selection and instance health management.

### 2. Invocation Name

`load_balancer_config`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `service_name` | `string` | Yes | Target service name | `"api-gateway"` |
| `action` | `string` | Yes | `"get"`, `"set_strategy"`, or `"set_health"` | `"set_strategy"` |
| `strategy` | `string` | No | Strategy name (required for `set_strategy`) | `"least_connections"` |
| `instance_id` | `string` | No | Instance ID (required for `set_health`) | `"svc-3"` |
| `healthy` | `boolean` | No | Health status (required for `set_health`) | `false` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"success"` or `"error"` | `"success"` |
| `service_name` | `string` | Service affected | `"api-gateway"` |
| `strategy` | `string` | Current strategy | `"least_connections"` |
| `instance_count` | `integer` | Registered instances | `4` |
| `healthy_count` | `integer` | Healthy instances | `3` |

### 5. Error Handling

- **Invalid Strategy**: Returns error if strategy name is not one of the supported values.
- **Service Not Found**: Returns error if service_name is not registered.
- **Missing Parameters**: Returns error if required parameters for the action are absent.

### 6. Idempotency

- **Idempotent**: Yes for `get` and `set_strategy`. `set_health` is idempotent (setting same value is a no-op).

### 7. Usage Examples

```json
{
  "tool_name": "load_balancer_config",
  "arguments": {
    "service_name": "api-gateway",
    "action": "set_strategy",
    "strategy": "weighted"
  }
}
```

```json
{
  "tool_name": "load_balancer_config",
  "arguments": {
    "service_name": "api-gateway",
    "action": "set_health",
    "instance_id": "svc-3",
    "healthy": false
  }
}
```

### 8. Security Considerations

- **Write Operations**: `set_strategy` and `set_health` modify runtime behavior. Restrict to authorized operators.
- **Validation**: Strategy values are validated against `LoadBalancerStrategy` enum.

---

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Home**: [Root README](../../../README.md)
