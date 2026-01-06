# Codomyrmex Agents — src/codomyrmex/agents/theory

## Signposting
- **Parent**: [agents](../AGENTS.md)
- **Self**: [Theory Agents](AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Theory submodule providing theoretical foundations for agentic systems. This includes agent architecture patterns (reactive, deliberative, hybrid) and reasoning models (symbolic, neural, hybrid).

## Function Signatures

### Agent Architectures

```python
def perceive(self, environment: dict[str, Any]) -> dict[str, Any]
```

Perceive the environment.

**Parameters:**
- `environment` (dict): Environment state

**Returns:** `dict` - Perceived information

```python
def decide(self, perception: dict[str, Any]) -> dict[str, Any]
```

Make a decision based on perception.

**Parameters:**
- `perception` (dict): Perceived information

**Returns:** `dict` - Decision/action

```python
def act(self, decision: dict[str, Any]) -> dict[str, Any]
```

Execute an action.

**Parameters:**
- `decision` (dict): Decision/action to execute

**Returns:** `dict` - Action result

### Reasoning Models

```python
def reason(self, premises: dict[str, Any], context: Optional[dict[str, Any]] = None) -> dict[str, Any]
```

Perform reasoning.

**Parameters:**
- `premises` (dict): Input premises/facts
- `context` (Optional[dict]): Optional context

**Returns:** `dict` - Reasoning result

```python
def explain(self, result: dict[str, Any]) -> str
```

Explain reasoning result.

**Parameters:**
- `result` (dict): Reasoning result

**Returns:** `str` - Explanation string

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Parent Module**: [agents](../AGENTS.md)



## Active Components
- `README.md` - Component file.
- `SPEC.md` - Component file.
- `__init__.py` - Component file.
- `agent_architectures.py` - Component file.
- `reasoning_models.py` - Component file.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update task queues when necessary.
