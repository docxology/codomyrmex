"""Lifecycle and provider-failure regressions for AutonomousAgent."""

import pytest

from codomyrmex.agents.autonomous import AutonomousAgent


class _Endpoint:
    def __init__(self, *, start_error: bool = False, stop_error: bool = False) -> None:
        self.start_error = start_error
        self.stop_error = stop_error

    def start(self) -> None:
        if self.start_error:
            raise RuntimeError("start failed")

    def stop(self) -> None:
        if self.stop_error:
            raise RuntimeError("stop failed")


def _agent(endpoint: _Endpoint) -> AutonomousAgent:
    agent = object.__new__(AutonomousAgent)
    agent.identity = "test-agent"
    agent.persona = "test"
    agent.endpoint = endpoint
    agent.running = False
    return agent


def test_start_does_not_claim_running_when_endpoint_fails() -> None:
    agent = _agent(_Endpoint(start_error=True))

    with pytest.raises(RuntimeError, match="start failed"):
        agent.start()

    assert agent.running is False


def test_stop_preserves_running_state_when_endpoint_fails() -> None:
    agent = _agent(_Endpoint(stop_error=True))
    agent.running = True

    with pytest.raises(RuntimeError, match="stop failed"):
        agent.stop()

    assert agent.running is True
