"""Tests for codomyrmex.agents.agentic_seek.task_planner.

Zero-mock tests covering JSON plan parsing, plan validation,
topological ordering, and task name extraction.
"""

import pytest

from codomyrmex.agents.agentic_seek.agent_types import (
    AgenticSeekAgentType,
    AgenticSeekTaskStep,
)
from codomyrmex.agents.agentic_seek.task_planner import (
    AgenticSeekTaskPlanner,
    extract_task_names,
    get_execution_order,
    parse_plan_json,
    validate_plan,
)

# ===================================================================
# extract_task_names
# ===================================================================

class TestExtractTaskNames:
    def test_numbered_lines(self):
        text = "1. Write code\n2. Test code\n3. Deploy"
        names = extract_task_names(text)
        assert len(names) == 3

    def test_hash_headings(self):
        text = "## Task A\nSome description\n## Task B"
        names = extract_task_names(text)
        assert len(names) == 2
        assert "## Task A" in names

    def test_mixed_formats(self):
        text = "## Phase 1\n1. Step A\n\n## Phase 2\n2. Step B"
        names = extract_task_names(text)
        assert len(names) == 4

    def test_empty_text(self):
        assert extract_task_names("") == []

    def test_no_tasks(self):
        assert extract_task_names("Just some regular text") == []


# ===================================================================
# parse_plan_json
# ===================================================================

class TestParsePlanJson:
    def test_basic_plan(self):
        text = '```json\n{"plan": [{"agent": "coder", "id": 1, "task": "Write code"}]}\n```'
        steps = parse_plan_json(text)
        assert len(steps) == 1
        assert steps[0].agent_type is AgenticSeekAgentType.CODER
        assert steps[0].task_id == 1
        assert steps[0].description == "Write code"

    def test_multi_step_plan(self):
        text = '''```json
{
  "plan": [
    {"agent": "web", "id": 1, "task": "Search docs"},
    {"agent": "coder", "id": 2, "task": "Write script", "need": [1]},
    {"agent": "file", "id": 3, "task": "Save output", "need": [2]}
  ]
}
```'''
        steps = parse_plan_json(text)
        assert len(steps) == 3
        assert steps[0].agent_type is AgenticSeekAgentType.BROWSER  # "web" → BROWSER
        assert steps[1].dependencies == [1]
        assert steps[2].dependencies == [2]

    def test_web_maps_to_browser(self):
        text = '```json\n{"plan": [{"agent": "web", "id": 1, "task": "Browse"}]}\n```'
        steps = parse_plan_json(text)
        assert steps[0].agent_type is AgenticSeekAgentType.BROWSER

    def test_missing_field_raises(self):
        text = '```json\n{"plan": [{"agent": "coder", "id": 1}]}\n```'
        with pytest.raises(ValueError, match="missing required fields"):
            parse_plan_json(text)

    def test_unknown_agent_raises(self):
        text = '```json\n{"plan": [{"agent": "unknown_agent", "id": 1, "task": "Do stuff"}]}\n```'
        with pytest.raises(ValueError, match="Unknown agent type"):
            parse_plan_json(text)

    def test_no_json_returns_empty(self):
        assert parse_plan_json("Just some text") == []

    def test_raw_json_without_fence(self):
        text = '{"plan": [{"agent": "casual", "id": 1, "task": "Chat"}]}'
        steps = parse_plan_json(text)
        assert len(steps) == 1

    def test_need_as_single_int(self):
        text = '```json\n{"plan": [{"agent": "coder", "id": 1, "task": "A"}, {"agent": "file", "id": 2, "task": "B", "need": 1}]}\n```'
        steps = parse_plan_json(text)
        assert steps[1].dependencies == [1]


# ===================================================================
# validate_plan
# ===================================================================

class TestValidatePlan:
    def test_valid_plan_no_errors(self):
        steps = [
            AgenticSeekTaskStep(AgenticSeekAgentType.CODER, 1, "Code"),
            AgenticSeekTaskStep(AgenticSeekAgentType.FILE, 2, "Save", dependencies=[1]),
        ]
        errors = validate_plan(steps)
        assert errors == []

    def test_missing_dependency(self):
        steps = [
            AgenticSeekTaskStep(AgenticSeekAgentType.CODER, 1, "Code", dependencies=[99]),
        ]
        errors = validate_plan(steps)
        assert any("99" in e for e in errors)

    def test_unavailable_agent(self):
        steps = [
            AgenticSeekTaskStep(AgenticSeekAgentType.BROWSER, 1, "Browse"),
        ]
        errors = validate_plan(
            steps,
            available_agents={AgenticSeekAgentType.CODER},
        )
        assert any("browser" in e for e in errors)

    def test_circular_dependency(self):
        steps = [
            AgenticSeekTaskStep(AgenticSeekAgentType.CODER, 1, "A", dependencies=[2]),
            AgenticSeekTaskStep(AgenticSeekAgentType.CODER, 2, "B", dependencies=[1]),
        ]
        errors = validate_plan(steps)
        assert any("Circular" in e for e in errors)

    def test_duplicate_ids(self):
        steps = [
            AgenticSeekTaskStep(AgenticSeekAgentType.CODER, 1, "A"),
            AgenticSeekTaskStep(AgenticSeekAgentType.CODER, 1, "B"),
        ]
        errors = validate_plan(steps)
        assert any("Duplicate" in e for e in errors)

    def test_empty_plan_is_valid(self):
        assert validate_plan([]) == []


# ===================================================================
# get_execution_order
# ===================================================================

class TestGetExecutionOrder:
    def test_simple_chain(self):
        steps = [
            AgenticSeekTaskStep(AgenticSeekAgentType.CODER, 1, "First"),
            AgenticSeekTaskStep(AgenticSeekAgentType.FILE, 2, "Second", dependencies=[1]),
            AgenticSeekTaskStep(AgenticSeekAgentType.CASUAL, 3, "Third", dependencies=[2]),
        ]
        ordered = get_execution_order(steps)
        ids = [s.task_id for s in ordered]
        assert ids == [1, 2, 3]

    def test_parallel_tasks(self):
        steps = [
            AgenticSeekTaskStep(AgenticSeekAgentType.CODER, 1, "A"),
            AgenticSeekTaskStep(AgenticSeekAgentType.BROWSER, 2, "B"),
            AgenticSeekTaskStep(AgenticSeekAgentType.FILE, 3, "C", dependencies=[1, 2]),
        ]
        ordered = get_execution_order(steps)
        ids = [s.task_id for s in ordered]
        # 1 and 2 must come before 3
        assert ids.index(3) > ids.index(1)
        assert ids.index(3) > ids.index(2)

    def test_empty_plan(self):
        assert get_execution_order([]) == []

    def test_cycle_raises(self):
        steps = [
            AgenticSeekTaskStep(AgenticSeekAgentType.CODER, 1, "A", dependencies=[2]),
            AgenticSeekTaskStep(AgenticSeekAgentType.CODER, 2, "B", dependencies=[1]),
        ]
        with pytest.raises(ValueError, match="Circular"):
            get_execution_order(steps)

    def test_single_step(self):
        steps = [AgenticSeekTaskStep(AgenticSeekAgentType.CASUAL, 1, "Only")]
        ordered = get_execution_order(steps)
        assert len(ordered) == 1
        assert ordered[0].task_id == 1


# ===================================================================
# AgenticSeekTaskPlanner facade
# ===================================================================

class TestAgenticSeekTaskPlanner:
    def test_parse(self):
        planner = AgenticSeekTaskPlanner()
        text = '```json\n{"plan": [{"agent": "coder", "id": 1, "task": "Code"}]}\n```'
        steps = planner.parse(text)
        assert len(steps) == 1

    def test_validate(self):
        planner = AgenticSeekTaskPlanner()
        steps = [AgenticSeekTaskStep(AgenticSeekAgentType.CODER, 1, "Code")]
        assert planner.validate(steps) == []

    def test_execution_order(self):
        planner = AgenticSeekTaskPlanner()
        steps = [
            AgenticSeekTaskStep(AgenticSeekAgentType.CODER, 1, "First"),
            AgenticSeekTaskStep(AgenticSeekAgentType.FILE, 2, "Second", dependencies=[1]),
        ]
        ordered = planner.execution_order(steps)
        assert ordered[0].task_id == 1

    def test_extract_names(self):
        planner = AgenticSeekTaskPlanner()
        names = planner.extract_names("1. Task A\n2. Task B")
        assert len(names) == 2
