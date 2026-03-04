# Agents / AgenticSeek Tests

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `agents/agentic_seek` sub-module. Covers agent routing, agent types and configuration data classes, client structure, code execution helpers, and task planning.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestClassifyQueryKeywords` | Keyword-based query classification to agent types |
| `TestClassifyQueryHeuristics` | Heuristic routing (code fences, URLs, file paths) |
| `TestClassifyQueryEdgeCases` | Edge cases for empty/whitespace input and custom defaults |
| `TestEstimateComplexity` | Prompt complexity estimation (low vs high) |
| `TestScoreHelper` | Internal score helper for keyword matching |
| `TestAgenticSeekAgentType` | AgentType enum members and from_string parsing |
| `TestAgenticSeekProvider` | Provider enum values (Ollama, server, etc.) |
| `TestAgenticSeekConfig` | Config dataclass construction, freezing, to_ini_dict |
| `TestAgenticSeekMemoryEntry` | Memory entry construction and to_dict |
| `TestAgenticSeekTaskStatus` | TaskStatus enum members |
| `TestAgenticSeekTaskStep` | TaskStep dataclass with dependencies |
| `TestAgenticSeekExecutionResult` | ExecutionResult string representation |
| `TestAgenticSeekClientStructure` | Client class methods and instantiation |
| `TestGetAvailableAgents` | Available agent listing |
| `TestClassifyQuery` | Client-level query classification |
| `TestValidateEnvironment` | Environment validation dict structure |
| `TestParseConfigIni` | INI config file parsing and defaults |
| `TestModuleImport` | Module import structure |
| `TestExtractCodeBlocks` | Code block extraction from markdown |
| `TestClassifyLanguage` | Language alias resolution |
| `TestBuildExecutionCommand` | Execution command construction per language |
| `TestParseExecutionOutput` | Execution output parsing (success/error detection) |
| `TestExtractTaskNames` | Task name extraction from numbered/heading lists |
| `TestParsePlanJson` | JSON plan parsing with agent mapping |
| `TestValidatePlan` | Plan validation (missing deps, circular deps, duplicates) |
| `TestGetExecutionOrder` | Topological execution order calculation |
| `TestAgenticSeekTaskPlanner` | TaskPlanner parse integration |

## Test Structure

```
tests/unit/agents/agentic_seek/
    __init__.py
    test_agent_router.py    # Query classification and routing
    test_agent_types.py     # Data classes and enums
    test_agentic_seek_client.py  # Client API surface
    test_code_execution.py  # Code block extraction and execution
    test_task_planner.py    # Task planning and dependency ordering
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/agents/agentic_seek/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/agents/agentic_seek/ --cov=src/codomyrmex/agents/agentic_seek -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../agents/agentic_seek/README.md)
- [All Tests](../../README.md)
