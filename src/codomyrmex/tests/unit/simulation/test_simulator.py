"""Unit tests for the simulation module.

Comprehensive tests covering:
- Action dataclass
- Agent base class (via concrete subclasses)
- RandomAgent behavior
- RuleBasedAgent behavior
- QLearningAgent behavior
- SimulationConfig
- SimulationResult
- Simulator engine lifecycle
"""

import pytest

from codomyrmex.simulation.agent import (
    Action,
    Agent,
    QLearningAgent,
    RandomAgent,
    RuleBasedAgent,
)
from codomyrmex.simulation.simulator import SimulationConfig, SimulationResult, Simulator


class ConcreteAgent(Agent):
    """A simple concrete agent for testing the abstract base class."""

    def act(self, observation):
        return Action(type="move", parameters={"x": 1, "y": 1})


# ---------------------------------------------------------------------------
# Action dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAction:
    """Tests for the Action dataclass."""

    def test_action_creation_with_defaults(self):
        """Action created with type only gets empty params and a timestamp."""
        action = Action(type="move")
        assert action.type == "move"
        assert action.parameters == {}
        assert action.timestamp > 0

    def test_action_creation_with_parameters(self):
        """Action stores custom parameters dict."""
        params = {"x": 10, "y": 20, "speed": 5.0}
        action = Action(type="attack", parameters=params)
        assert action.parameters == params

    def test_action_type_is_string(self):
        """Action type is stored as the provided string."""
        action = Action(type="special_ability")
        assert isinstance(action.type, str)
        assert action.type == "special_ability"

    def test_action_timestamp_auto_generated(self):
        """Two actions created in sequence have non-decreasing timestamps."""
        a1 = Action(type="first")
        a2 = Action(type="second")
        assert a2.timestamp >= a1.timestamp

    def test_action_empty_type(self):
        """Empty string type is valid."""
        action = Action(type="")
        assert action.type == ""


# ---------------------------------------------------------------------------
# Agent base class
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAgentBase:
    """Tests for the Agent abstract base class via ConcreteAgent."""

    def test_agent_initialization_with_id_only(self):
        """Agent with ID only sets name to ID."""
        agent = ConcreteAgent(agent_id="a1")
        assert agent.id == "a1"
        assert agent.name == "a1"
        assert agent.step_count == 0
        assert len(agent._history) == 0

    def test_agent_initialization_with_name(self):
        """Agent with explicit name uses that name."""
        agent = ConcreteAgent(agent_id="a1", name="Alice")
        assert agent.id == "a1"
        assert agent.name == "Alice"

    def test_agent_record_action(self):
        """record_action appends to history and increments step_count."""
        agent = ConcreteAgent("a1")
        action = Action(type="test")
        agent.record_action(action)
        assert agent.step_count == 1
        assert len(agent._history) == 1
        assert agent._history[0] is action

    def test_agent_record_multiple_actions(self):
        """Multiple actions are recorded in order."""
        agent = ConcreteAgent("a1")
        for i in range(5):
            agent.record_action(Action(type=f"action_{i}"))
        assert agent.step_count == 5
        assert agent._history[0].type == "action_0"
        assert agent._history[4].type == "action_4"

    def test_agent_reset(self):
        """reset() clears history and step_count."""
        agent = ConcreteAgent("a1")
        agent.record_action(Action(type="test"))
        agent.record_action(Action(type="test2"))
        agent.reset()
        assert agent.step_count == 0
        assert len(agent._history) == 0

    def test_agent_history_returns_copy(self):
        """history property returns a copy, not the internal list."""
        agent = ConcreteAgent("a1")
        agent.record_action(Action(type="test"))
        h1 = agent.history
        h2 = agent.history
        assert h1 is not h2
        assert h1 == h2

    def test_agent_last_action_when_empty(self):
        """last_action is None before any actions."""
        agent = ConcreteAgent("a1")
        assert agent.last_action is None

    def test_agent_last_action_after_recording(self):
        """last_action returns the most recent action."""
        agent = ConcreteAgent("a1")
        agent.record_action(Action(type="first"))
        agent.record_action(Action(type="second"))
        assert agent.last_action.type == "second"

    def test_agent_to_dict(self):
        """to_dict returns agent state as dict with correct keys."""
        agent = ConcreteAgent("a1", name="Alice")
        agent.record_action(Action(type="test"))
        d = agent.to_dict()
        assert d["id"] == "a1"
        assert d["name"] == "Alice"
        assert d["type"] == "ConcreteAgent"
        assert d["step_count"] == 1
        assert d["history_length"] == 1

    def test_agent_cannot_instantiate_abstract(self):
        """Cannot instantiate Agent directly."""
        with pytest.raises(TypeError):
            Agent(agent_id="raw")


# ---------------------------------------------------------------------------
# RandomAgent
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRandomAgent:
    """Tests for RandomAgent."""

    def test_default_action_types(self):
        """Default action types include move, wait, observe."""
        agent = RandomAgent("r1")
        assert set(agent.action_types) == {"move", "wait", "observe"}

    def test_custom_action_types(self):
        """Custom action types are stored."""
        agent = RandomAgent("r1", action_types=["attack", "defend"])
        assert agent.action_types == ["attack", "defend"]

    def test_act_returns_valid_action(self):
        """act() returns an Action with type from action_types."""
        agent = RandomAgent("r1", action_types=["a", "b", "c"])
        action = agent.act({})
        assert isinstance(action, Action)
        assert action.type in ["a", "b", "c"]

    def test_act_returns_varied_actions_over_many_calls(self):
        """Over many calls, multiple action types should appear."""
        agent = RandomAgent("r1", action_types=["x", "y", "z"])
        types_seen = set()
        for _ in range(100):
            action = agent.act({})
            types_seen.add(action.type)
        assert len(types_seen) >= 2

    def test_random_agent_inherits_agent(self):
        """RandomAgent is an instance of Agent."""
        agent = RandomAgent("r1")
        assert isinstance(agent, Agent)

    def test_random_agent_name_defaults_to_id(self):
        """RandomAgent name defaults to agent_id when not provided."""
        agent = RandomAgent("r1")
        assert agent.name == "r1"

    def test_random_agent_with_name(self):
        """RandomAgent stores explicit name."""
        agent = RandomAgent("r1", name="Random Bob")
        assert agent.name == "Random Bob"

    def test_random_agent_single_action_type(self):
        """RandomAgent with one action type always returns that type."""
        agent = RandomAgent("r1", action_types=["only"])
        for _ in range(10):
            assert agent.act({}).type == "only"


# ---------------------------------------------------------------------------
# RuleBasedAgent
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRuleBasedAgent:
    """Tests for RuleBasedAgent."""

    def test_no_rules_returns_idle(self):
        """With no rules, act() returns 'idle'."""
        agent = RuleBasedAgent("rb1")
        action = agent.act({})
        assert action.type == "idle"

    def test_single_matching_rule(self):
        """A matching rule fires."""
        agent = RuleBasedAgent("rb1")
        agent.add_rule(lambda obs: True, "patrol")
        action = agent.act({})
        assert action.type == "patrol"

    def test_priority_order(self):
        """First matching rule takes priority."""
        agent = RuleBasedAgent("rb1")
        agent.add_rule(lambda obs: obs.get("threat"), "defend")
        agent.add_rule(lambda obs: True, "patrol")
        action = agent.act({"threat": True})
        assert action.type == "defend"

    def test_fallthrough_to_second_rule(self):
        """When first rule does not match, second rule fires."""
        agent = RuleBasedAgent("rb1")
        agent.add_rule(lambda obs: obs.get("threat"), "defend")
        agent.add_rule(lambda obs: True, "patrol")
        action = agent.act({"threat": False})
        assert action.type == "patrol"

    def test_rule_with_params(self):
        """Rule can include custom parameters in the action."""
        agent = RuleBasedAgent("rb1")
        agent.add_rule(lambda obs: True, "attack", {"target": "enemy"})
        action = agent.act({})
        assert action.type == "attack"
        assert action.parameters["target"] == "enemy"

    def test_failing_condition_is_skipped(self):
        """A rule whose condition raises an exception is skipped."""
        agent = RuleBasedAgent("rb1")
        agent.add_rule(lambda obs: 1 / 0, "crash")
        agent.add_rule(lambda obs: True, "safe")
        action = agent.act({})
        assert action.type == "safe"

    def test_all_conditions_fail_returns_idle(self):
        """When all conditions raise exceptions, idle is returned."""
        agent = RuleBasedAgent("rb1")
        agent.add_rule(lambda obs: 1 / 0, "crash1")
        agent.add_rule(lambda obs: obs["missing"], "crash2")
        action = agent.act({})
        assert action.type == "idle"

    def test_inherits_agent(self):
        """RuleBasedAgent is an Agent instance."""
        assert isinstance(RuleBasedAgent("rb1"), Agent)


# ---------------------------------------------------------------------------
# QLearningAgent
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestQLearningAgent:
    """Tests for QLearningAgent."""

    def test_initialization_defaults(self):
        """QLearningAgent has correct defaults."""
        agent = QLearningAgent("ql1", action_types=["a", "b"])
        assert agent.alpha == 0.1
        assert agent.gamma == 0.99
        assert agent.epsilon == 1.0
        assert agent.q_table_size == 0

    def test_act_returns_valid_action(self):
        """act() returns an Action with type from action_types."""
        agent = QLearningAgent("ql1", action_types=["up", "down"])
        action = agent.act({"pos": 0})
        assert action.type in ["up", "down"]

    def test_act_sets_last_state(self):
        """act() sets _last_state and _last_action_type for learn()."""
        agent = QLearningAgent("ql1", action_types=["a"])
        assert agent._last_state is None
        agent.act({"x": 1})
        assert agent._last_state is not None
        assert agent._last_action_type in ["a"]

    def test_learn_updates_q_value(self):
        """learn() changes Q-value for the last state-action pair."""
        agent = QLearningAgent("ql1", action_types=["a"], alpha=0.5, epsilon=0.0)
        obs = {"x": 1}
        agent.act(obs)
        q_before = agent.get_q_values(obs)["a"]
        agent.learn(10.0)
        q_after = agent.get_q_values(obs)["a"]
        assert q_after > q_before

    def test_learn_without_prior_act_is_noop(self):
        """learn() does nothing if act() hasn't been called."""
        agent = QLearningAgent("ql1", action_types=["a"])
        agent.learn(10.0)
        assert agent.q_table_size == 0

    def test_epsilon_decays_on_learn(self):
        """epsilon decays each time learn() is called."""
        agent = QLearningAgent(
            "ql1", action_types=["a"], epsilon=1.0, epsilon_decay=0.9
        )
        agent.act({"x": 1})
        agent.learn(1.0)
        assert agent.epsilon < 1.0
        assert agent.epsilon == pytest.approx(0.9)

    def test_epsilon_does_not_decay_below_min(self):
        """epsilon never goes below epsilon_min."""
        agent = QLearningAgent(
            "ql1", action_types=["a"],
            epsilon=0.02, epsilon_decay=0.5, epsilon_min=0.01,
        )
        agent.act({"x": 1})
        agent.learn(1.0)
        assert agent.epsilon == 0.01

    def test_get_q_values_returns_copy(self):
        """get_q_values returns a new dict, not the internal one."""
        agent = QLearningAgent("ql1", action_types=["a", "b"])
        agent.act({"x": 1})
        q1 = agent.get_q_values({"x": 1})
        q2 = agent.get_q_values({"x": 1})
        assert q1 is not q2

    def test_greedy_exploitation(self):
        """With epsilon=0, agent always picks the best Q-value action."""
        agent = QLearningAgent(
            "ql1", action_types=["a", "b"], epsilon=0.0, alpha=1.0,
        )
        obs = {"s": 1}
        # Force Q("a") = 10 by acting and learning
        agent.epsilon = 0.0
        agent._q_table[agent._state_key(obs)]["a"] = 10.0
        agent._q_table[agent._state_key(obs)]["b"] = 1.0
        for _ in range(10):
            action = agent.act(obs)
            assert action.type == "a"

    def test_inherits_agent(self):
        """QLearningAgent is an Agent instance."""
        agent = QLearningAgent("ql1", action_types=["a"])
        assert isinstance(agent, Agent)


# ---------------------------------------------------------------------------
# SimulationConfig
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSimulationConfig:
    """Tests for the SimulationConfig dataclass."""

    def test_default_config(self):
        """Default config has sensible defaults."""
        config = SimulationConfig()
        assert config.name == "default_simulation"
        assert config.max_steps == 1000
        assert config.seed is None
        assert config.params == {}

    def test_custom_config(self):
        """Custom values are stored correctly."""
        config = SimulationConfig(
            name="test_sim", max_steps=50, seed=42, params={"lr": 0.01}
        )
        assert config.name == "test_sim"
        assert config.max_steps == 50
        assert config.seed == 42
        assert config.params["lr"] == 0.01

    def test_config_params_independent(self):
        """Each config instance has its own params dict."""
        c1 = SimulationConfig()
        c2 = SimulationConfig()
        c1.params["key"] = "val"
        assert "key" not in c2.params


# ---------------------------------------------------------------------------
# SimulationResult
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSimulationResult:
    """Tests for the SimulationResult dataclass."""

    def test_result_creation(self):
        """SimulationResult stores all provided fields."""
        result = SimulationResult(
            steps_completed=10, config_name="test",
            status="completed", agent_count=3,
        )
        assert result.steps_completed == 10
        assert result.config_name == "test"
        assert result.status == "completed"
        assert result.agent_count == 3
        assert result.history == []

    def test_result_with_history(self):
        """SimulationResult stores history entries."""
        result = SimulationResult(
            steps_completed=1, config_name="t",
            status="completed", agent_count=1,
            history=[{"step": 0, "data": "test"}],
        )
        assert len(result.history) == 1


# ---------------------------------------------------------------------------
# Simulator engine
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSimulator:
    """Tests for the Simulator engine."""

    def test_simulator_default_init(self):
        """Simulator with no arguments has default config and no agents."""
        sim = Simulator()
        assert sim.config.name == "default_simulation"
        assert len(sim.agents) == 0
        assert sim.step_count == 0

    def test_simulator_with_config(self):
        """Simulator uses provided config."""
        config = SimulationConfig(max_steps=10, name="custom")
        sim = Simulator(config)
        assert sim.config.max_steps == 10
        assert sim.config.name == "custom"

    def test_simulator_with_agents(self):
        """Simulator stores initial agents by ID."""
        agents = [ConcreteAgent("a1"), ConcreteAgent("a2")]
        sim = Simulator(agents=agents)
        assert "a1" in sim.agents
        assert "a2" in sim.agents
        assert len(sim.agents) == 2

    def test_add_agent(self):
        """add_agent adds agent to the simulator."""
        sim = Simulator()
        agent = ConcreteAgent("a1")
        sim.add_agent(agent)
        assert "a1" in sim.agents

    def test_add_duplicate_agent_raises(self):
        """add_agent raises ValueError for duplicate ID."""
        sim = Simulator()
        agent = ConcreteAgent("a1")
        sim.add_agent(agent)
        with pytest.raises(ValueError, match="already exists"):
            sim.add_agent(agent)

    def test_remove_agent(self):
        """remove_agent removes agent from the simulator."""
        sim = Simulator()
        agent = ConcreteAgent("a1")
        sim.add_agent(agent)
        sim.remove_agent("a1")
        assert "a1" not in sim.agents

    def test_remove_nonexistent_agent_no_error(self):
        """remove_agent with unknown ID does not raise."""
        sim = Simulator()
        sim.remove_agent("nonexistent")

    def test_run_simulation(self):
        """run() executes steps and returns results."""
        config = SimulationConfig(max_steps=5)
        agent = ConcreteAgent("a1")
        sim = Simulator(config, agents=[agent])
        result = sim.run()
        assert result.steps_completed == 5
        assert result.status == "completed"
        assert result.agent_count == 1
        assert agent.step_count == 5

    def test_run_records_agent_history(self):
        """run() causes agents to record actions."""
        config = SimulationConfig(max_steps=3)
        agent = ConcreteAgent("a1")
        sim = Simulator(config, agents=[agent])
        sim.run()
        assert len(agent._history) == 3
        assert all(a.type == "move" for a in agent._history)

    def test_run_with_multiple_agents(self):
        """run() processes all agents each step."""
        config = SimulationConfig(max_steps=5)
        a1 = ConcreteAgent("a1")
        a2 = ConcreteAgent("a2")
        sim = Simulator(config, agents=[a1, a2])
        result = sim.run()
        assert result.agent_count == 2
        assert a1.step_count == 5
        assert a2.step_count == 5

    def test_run_with_no_agents(self):
        """run() completes even with no agents."""
        config = SimulationConfig(max_steps=3)
        sim = Simulator(config)
        result = sim.run()
        assert result.steps_completed == 3
        assert result.agent_count == 0

    def test_run_updates_environment_state(self):
        """run() updates environment state with agent actions."""
        config = SimulationConfig(max_steps=1)
        agent = ConcreteAgent("a1")
        sim = Simulator(config, agents=[agent])
        sim.run()
        assert "last_action_a1" in sim._environment_state

    def test_step_single(self):
        """A single step() call processes agents."""
        sim = Simulator(agents=[ConcreteAgent("a1")])
        sim.step()
        assert sim.agents["a1"].step_count == 1

    def test_get_results_while_running(self):
        """get_results returns current state."""
        sim = Simulator(agents=[ConcreteAgent("a1")])
        result = sim.get_results()
        assert result.steps_completed == 0
        assert result.agent_count == 1

    def test_run_with_random_agent(self):
        """Simulation with RandomAgent completes."""
        config = SimulationConfig(max_steps=10)
        agent = RandomAgent("r1", action_types=["move", "wait"])
        sim = Simulator(config, agents=[agent])
        result = sim.run()
        assert result.steps_completed == 10
        assert agent.step_count == 10

    def test_run_with_rule_based_agent(self):
        """Simulation with RuleBasedAgent completes."""
        config = SimulationConfig(max_steps=5)
        agent = RuleBasedAgent("rb1")
        agent.add_rule(lambda obs: True, "patrol")
        sim = Simulator(config, agents=[agent])
        result = sim.run()
        assert result.steps_completed == 5
        assert all(a.type == "patrol" for a in agent._history)

    def test_run_with_qlearning_agent(self):
        """Simulation with QLearningAgent completes and learns."""
        config = SimulationConfig(max_steps=10)
        agent = QLearningAgent("ql1", action_types=["a", "b"])
        sim = Simulator(config, agents=[agent])
        result = sim.run()
        assert result.steps_completed == 10
        assert agent.step_count == 10
