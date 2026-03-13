"""Unit tests for the HTN Hierarchical Planner.

Zero-Mock Policy: Constructs an authentic logistics and mathematics
mockless domain to exhaustively simulate state mutation and verify recursive
path resolutions without mock assertions.
"""

import pytest

from codomyrmex.orchestrator.htn_planner import HTNPlanner, Method, Operator, State


@pytest.fixture
def test_domain():
    """Create a standard logistics/movement domain for testing HTN."""
    planner = HTNPlanner()

    # Primitive: Move between two connected locations
    def move_action(state, loc_from, loc_to):
        if (
            state.facts["at"] == loc_from
            and loc_to in state.facts["connected"][loc_from]
        ):
            state.facts["at"] = loc_to
            return True
        return False

    planner.add_operator(Operator("move", move_action))

    # Compound: Travel to a destination
    def travel_preconditions(state, dest):
        return True  # Pathfinding determines success

    def travel_subtasks(state, dest):
        current_loc = state.facts["at"]
        if current_loc == dest:
            return []  # Already there

        if dest in state.facts["connected"][current_loc]:
            return [("move", current_loc, dest)]

        for intermediate in state.facts["connected"][current_loc]:
            if dest in state.facts["connected"][intermediate]:
                return [("move", current_loc, intermediate), ("travel", dest)]

        return [("fail_travel",)]

    planner.add_method(
        "travel", Method("travel_method", travel_preconditions, travel_subtasks)
    )

    return planner


@pytest.mark.unit
def test_htn_planner_primitive_success(test_domain):
    """Test executing a simple primitive operator plan."""
    initial_state = State(
        facts={"at": "A", "connected": {"A": ["B"], "B": ["C"], "C": []}}
    )

    plan = test_domain.plan(initial_state, [("move", "A", "B")])
    assert plan == [("move", "A", "B")]


@pytest.mark.unit
def test_htn_planner_primitive_fail(test_domain):
    """Test primitive operator fails preconditions."""
    initial_state = State(
        facts={"at": "A", "connected": {"A": ["B"], "B": ["C"], "C": []}}
    )

    # C is not directly connected to A
    plan = test_domain.plan(initial_state, [("move", "A", "C")])
    assert plan is None


@pytest.mark.unit
def test_htn_planner_compound_decomposition(test_domain):
    """Test compound task recursively finding path using methods."""
    initial_state = State(
        facts={"at": "A", "connected": {"A": ["B"], "B": ["C"], "C": []}}
    )

    plan = test_domain.plan(initial_state, [("travel", "C")])
    assert plan == [("move", "A", "B"), ("move", "B", "C")]


@pytest.mark.unit
def test_htn_planner_impossible_compound(test_domain):
    """Test failure of compound task when decomposition cannot resolve."""
    initial_state = State(
        facts={"at": "A", "connected": {"A": ["B"], "B": ["C"], "C": []}}
    )

    plan = test_domain.plan(initial_state, [("travel", "Z")])
    assert plan is None


@pytest.mark.unit
def test_htn_planner_backtracking():
    """Test planner correctly backtracks state when a path fails."""
    planner = HTNPlanner()

    def modify_counter(state, amount):
        state.facts["counter"] += amount
        return True

    def check_goal(state, target):
        return state.facts["counter"] == target

    planner.add_operator(Operator("add", modify_counter))
    planner.add_operator(Operator("check", check_goal))

    def try_both_paths(state, target):
        return True

    def path_1(state, target):
        return [("add", 5), ("check", target)]

    def path_2(state, target):
        return [("add", 10), ("check", target)]

    planner.add_method("solve", Method("option_1", try_both_paths, path_1))
    planner.add_method("solve", Method("option_2", try_both_paths, path_2))

    initial_state = State(facts={"counter": 0})

    # Option 1 fails constraint; Option 2 satisfies target=10
    plan = planner.plan(initial_state, [("solve", 10)])

    assert plan == [("add", 10), ("check", 10)]
