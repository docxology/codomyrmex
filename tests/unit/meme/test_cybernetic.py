"""Tests for meme.cybernetic -- zero-mock, real instances only.

Covers FeedbackType, SystemState, FeedbackLoop, ControlSystem, PIDController,
apply_control, and CyberneticEngine with real computation.
"""

from __future__ import annotations

import pytest

from codomyrmex.meme.cybernetic.control import PIDController, apply_control
from codomyrmex.meme.cybernetic.engine import CyberneticEngine
from codomyrmex.meme.cybernetic.models import (
    ControlSystem,
    FeedbackLoop,
    FeedbackType,
    Homeostat,
    SystemState,
)

# ---------------------------------------------------------------------------
# FeedbackType enum
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestFeedbackType:
    """Tests for the FeedbackType enum."""

    def test_two_types_present(self) -> None:
        """POSITIVE and NEGATIVE are present."""
        values = {ft.value for ft in FeedbackType}
        assert values == {"positive", "negative"}

    def test_str_subclass(self) -> None:
        """FeedbackType is a StrEnum."""
        assert isinstance(FeedbackType.POSITIVE, str)
        assert FeedbackType.NEGATIVE == "negative"


# ---------------------------------------------------------------------------
# SystemState dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSystemState:
    """Tests for the SystemState dataclass."""

    def test_empty_defaults(self) -> None:
        """Default SystemState has empty variables dict."""
        state = SystemState()
        assert state.variables == {}

    def test_variables_stored(self) -> None:
        """Variables dict is stored and retrievable."""
        state = SystemState(variables={"temperature": 37.0, "pressure": 1.0})
        assert state.variables["temperature"] == pytest.approx(37.0)
        assert state.variables["pressure"] == pytest.approx(1.0)

    def test_timestamp_is_float(self) -> None:
        """timestamp is a non-zero float."""
        state = SystemState()
        assert isinstance(state.timestamp, float)
        assert state.timestamp > 0


# ---------------------------------------------------------------------------
# FeedbackLoop dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestFeedbackLoop:
    """Tests for the FeedbackLoop dataclass."""

    def test_creation_stores_fields(self) -> None:
        """All FeedbackLoop fields are stored correctly."""
        loop = FeedbackLoop(
            source_var="temperature",
            target_var="heating",
            gain=2.0,
            feedback_type=FeedbackType.NEGATIVE,
            delay=0.5,
        )
        assert loop.source_var == "temperature"
        assert loop.target_var == "heating"
        assert loop.gain == pytest.approx(2.0)
        assert loop.feedback_type == FeedbackType.NEGATIVE
        assert loop.delay == pytest.approx(0.5)

    def test_default_gain(self) -> None:
        """Default gain is 1.0."""
        loop = FeedbackLoop(source_var="x", target_var="y")
        assert loop.gain == pytest.approx(1.0)

    def test_default_feedback_type_negative(self) -> None:
        """Default feedback_type is NEGATIVE (stabilizing)."""
        loop = FeedbackLoop(source_var="x", target_var="y")
        assert loop.feedback_type == FeedbackType.NEGATIVE

    def test_default_delay_zero(self) -> None:
        """Default delay is 0.0."""
        loop = FeedbackLoop(source_var="x", target_var="y")
        assert loop.delay == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Homeostat dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestHomeostat:
    """Tests for the Homeostat dataclass."""

    def test_creation(self) -> None:
        """Homeostat stores essential_vars and bounds."""
        h = Homeostat(
            essential_vars=["temperature", "pressure"],
            bounds={"temperature": (36.5, 37.5)},
            adaptation_rate=0.05,
        )
        assert "temperature" in h.essential_vars
        assert h.bounds["temperature"] == (36.5, 37.5)
        assert h.adaptation_rate == pytest.approx(0.05)

    def test_default_adaptation_rate(self) -> None:
        """Default adaptation_rate is 0.1."""
        h = Homeostat(essential_vars=["x"])
        assert h.adaptation_rate == pytest.approx(0.1)


# ---------------------------------------------------------------------------
# ControlSystem dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestControlSystem:
    """Tests for the ControlSystem dataclass."""

    def test_creation_stores_fields(self) -> None:
        """All ControlSystem fields are stored."""
        cs = ControlSystem(name="thermostat", setpoints={"temperature": 22.0})
        assert cs.name == "thermostat"
        assert cs.setpoints["temperature"] == pytest.approx(22.0)
        assert cs.active is True

    def test_empty_setpoints_default(self) -> None:
        """Default setpoints is empty dict."""
        cs = ControlSystem(name="x")
        assert cs.setpoints == {}

    def test_inactive_system(self) -> None:
        """active=False is stored correctly."""
        cs = ControlSystem(name="x", active=False)
        assert cs.active is False


# ---------------------------------------------------------------------------
# PIDController
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPIDController:
    """Tests for the PIDController compute method."""

    def test_proportional_only_positive_error(self) -> None:
        """Pure P controller: setpoint=10, measured=8 gives positive output."""
        pid = PIDController(kp=1.0, ki=0.0, kd=0.0)
        output = pid.compute(setpoint=10.0, measured_value=8.0, dt=0.1)
        assert output == pytest.approx(2.0, abs=1e-9)

    def test_proportional_only_negative_error(self) -> None:
        """Pure P controller with overshoot gives negative output."""
        pid = PIDController(kp=1.0, ki=0.0, kd=0.0)
        output = pid.compute(setpoint=5.0, measured_value=7.0, dt=0.1)
        assert output == pytest.approx(-2.0, abs=1e-9)

    def test_zero_error_gives_zero_output(self) -> None:
        """When setpoint equals measured, output is zero."""
        pid = PIDController(kp=2.0, ki=0.0, kd=0.0)
        output = pid.compute(setpoint=5.0, measured_value=5.0, dt=0.1)
        assert output == pytest.approx(0.0, abs=1e-9)

    def test_integral_accumulates(self) -> None:
        """Integral term accumulates over multiple calls."""
        pid = PIDController(kp=0.0, ki=1.0, kd=0.0)
        # First call: integral = error * dt = 2.0 * 0.1 = 0.2, output = 0.2
        out1 = pid.compute(setpoint=10.0, measured_value=8.0, dt=0.1)
        # Second call: integral += 2.0 * 0.1 = 0.4 total, output = 0.4
        out2 = pid.compute(setpoint=10.0, measured_value=8.0, dt=0.1)
        assert out2 > out1

    def test_derivative_term(self) -> None:
        """Derivative term responds to error rate of change."""
        pid = PIDController(kp=0.0, ki=0.0, kd=1.0)
        # First call: last_error=0, new error=5, derivative=(5-0)/0.1=50
        out = pid.compute(setpoint=5.0, measured_value=0.0, dt=0.1)
        # d_term = 1.0 * 50.0 = 50.0
        assert out == pytest.approx(50.0, abs=1e-6)

    def test_combined_pid_output(self) -> None:
        """Combined PID computes sum of P, I, D terms."""
        pid = PIDController(kp=1.0, ki=0.5, kd=0.0)
        # error = 4, p = 4, integral = 4*0.1=0.4, i = 0.5*0.4=0.2
        out = pid.compute(setpoint=4.0, measured_value=0.0, dt=0.1)
        assert out == pytest.approx(4.2, abs=1e-9)


# ---------------------------------------------------------------------------
# apply_control
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestApplyControl:
    """Tests for the apply_control function."""

    def test_negative_feedback_reduces_value(self) -> None:
        """NEGATIVE feedback: current - (signal * gain)."""
        loop = FeedbackLoop(
            source_var="x",
            target_var="y",
            gain=2.0,
            feedback_type=FeedbackType.NEGATIVE,
        )
        result = apply_control(current_val=10.0, loop=loop, input_signal=1.5)
        assert result == pytest.approx(10.0 - 2.0 * 1.5, abs=1e-9)

    def test_positive_feedback_increases_value(self) -> None:
        """POSITIVE feedback: current + (signal * gain)."""
        loop = FeedbackLoop(
            source_var="x",
            target_var="y",
            gain=3.0,
            feedback_type=FeedbackType.POSITIVE,
        )
        result = apply_control(current_val=5.0, loop=loop, input_signal=2.0)
        assert result == pytest.approx(5.0 + 3.0 * 2.0, abs=1e-9)

    def test_zero_signal_returns_current_value(self) -> None:
        """Zero input signal returns current value unchanged."""
        loop = FeedbackLoop(source_var="x", target_var="y", gain=10.0)
        result = apply_control(current_val=7.0, loop=loop, input_signal=0.0)
        assert result == pytest.approx(7.0, abs=1e-9)

    def test_negative_feedback_unit_gain(self) -> None:
        """Unit gain negative feedback subtracts signal from current."""
        loop = FeedbackLoop(
            source_var="x",
            target_var="y",
            gain=1.0,
            feedback_type=FeedbackType.NEGATIVE,
        )
        result = apply_control(current_val=10.0, loop=loop, input_signal=3.0)
        assert result == pytest.approx(7.0, abs=1e-9)


# ---------------------------------------------------------------------------
# CyberneticEngine
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCyberneticEngineControllers:
    """Tests for CyberneticEngine controller management."""

    def test_add_controller_registers_it(self) -> None:
        """add_controller registers a PID for the variable."""
        engine = CyberneticEngine()
        engine.add_controller("temperature", kp=1.0, ki=0.0, kd=0.0)
        assert "temperature" in engine._controllers

    def test_add_multiple_controllers(self) -> None:
        """Multiple controllers can be added for different variables."""
        engine = CyberneticEngine()
        engine.add_controller("temperature")
        engine.add_controller("pressure")
        assert len(engine._controllers) == 2

    def test_add_controller_stores_params(self) -> None:
        """Registered controller has the specified gains."""
        engine = CyberneticEngine()
        engine.add_controller("x", kp=2.5, ki=0.5, kd=0.1)
        pid = engine._controllers["x"]
        assert pid.kp == pytest.approx(2.5)
        assert pid.ki == pytest.approx(0.5)
        assert pid.kd == pytest.approx(0.1)


@pytest.mark.unit
class TestCyberneticEngineUpdate:
    """Tests for CyberneticEngine.update."""

    def test_update_returns_dict(self) -> None:
        """update returns a dict of control signals."""
        engine = CyberneticEngine()
        engine.add_controller("temperature")
        system = ControlSystem(name="test", setpoints={"temperature": 20.0})
        state = SystemState(variables={"temperature": 15.0})
        outputs = engine.update(system, state)
        assert isinstance(outputs, dict)

    def test_update_output_for_registered_variable(self) -> None:
        """update produces output for registered controlled variable."""
        engine = CyberneticEngine()
        engine.add_controller("temperature", kp=1.0, ki=0.0, kd=0.0)
        system = ControlSystem(name="test", setpoints={"temperature": 20.0})
        state = SystemState(variables={"temperature": 15.0})
        outputs = engine.update(system, state)
        assert "temperature" in outputs

    def test_update_no_output_for_unregistered_variable(self) -> None:
        """update skips variables without registered controllers."""
        engine = CyberneticEngine()
        # No controller for 'pressure'
        system = ControlSystem(name="test", setpoints={"pressure": 1.0})
        state = SystemState(variables={"pressure": 0.5})
        outputs = engine.update(system, state)
        assert "pressure" not in outputs

    def test_update_positive_error_gives_positive_signal(self) -> None:
        """When measured < setpoint, P controller gives positive output."""
        engine = CyberneticEngine()
        engine.add_controller("x", kp=1.0, ki=0.0, kd=0.0)
        system = ControlSystem(name="test", setpoints={"x": 10.0})
        state = SystemState(variables={"x": 5.0})
        outputs = engine.update(system, state)
        assert outputs["x"] > 0.0

    def test_update_empty_setpoints_gives_empty_output(self) -> None:
        """System with no setpoints produces no outputs."""
        engine = CyberneticEngine()
        engine.add_controller("x")
        system = ControlSystem(name="test", setpoints={})
        state = SystemState(variables={"x": 5.0})
        outputs = engine.update(system, state)
        assert outputs == {}
