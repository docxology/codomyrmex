"""Tests for codomyrmex.defense.defense — Severity, RateLimiter, ThreatDetector, Defense."""

import time

import pytest

from codomyrmex.defense.defense import (
    Defense,
    DetectionRule,
    RateLimiter,
    ResponseAction,
    Severity,
    ThreatDetector,
    ThreatEvent,
    create_defense,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSeverity:
    """Tests for the Severity enum."""

    def test_all_levels(self):
        """All five severity levels exist with correct values."""
        assert Severity.INFO.value == "info"
        assert Severity.LOW.value == "low"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.HIGH.value == "high"
        assert Severity.CRITICAL.value == "critical"

    def test_count(self):
        """Exactly five severity levels."""
        assert len(Severity) == 5


@pytest.mark.unit
class TestResponseAction:
    """Tests for the ResponseAction enum."""

    def test_all_actions(self):
        """All response actions exist."""
        assert ResponseAction.LOG.value == "log"
        assert ResponseAction.THROTTLE.value == "throttle"
        assert ResponseAction.BLOCK.value == "block"
        assert ResponseAction.ALERT.value == "alert"
        assert ResponseAction.QUARANTINE.value == "quarantine"

    def test_count(self):
        """Exactly five response actions."""
        assert len(ResponseAction) == 5


# ---------------------------------------------------------------------------
# ThreatEvent dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestThreatEvent:
    """Tests for the ThreatEvent dataclass."""

    def test_creation(self):
        """Basic ThreatEvent instantiation."""
        evt = ThreatEvent(
            source="10.0.0.1",
            category="brute_force",
            severity=Severity.HIGH,
            description="Multiple failed logins",
        )
        assert evt.source == "10.0.0.1"
        assert evt.category == "brute_force"
        assert evt.severity == Severity.HIGH
        assert evt.timestamp > 0
        assert evt.metadata == {}
        assert evt.response is None

    def test_with_metadata_and_response(self):
        """ThreatEvent with optional fields."""
        evt = ThreatEvent(
            source="s",
            category="c",
            severity=Severity.LOW,
            description="d",
            metadata={"key": "val"},
            response=ResponseAction.BLOCK,
        )
        assert evt.metadata["key"] == "val"
        assert evt.response == ResponseAction.BLOCK


# ---------------------------------------------------------------------------
# RateLimiter
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRateLimiter:
    """Tests for the RateLimiter sliding-window implementation."""

    def test_allow_under_limit(self):
        """Requests under the limit are allowed."""
        rl = RateLimiter(max_requests=5, window_seconds=60.0)
        for _ in range(5):
            assert rl.allow("ip1") is True

    def test_deny_over_limit(self):
        """The request that exceeds the limit is denied."""
        rl = RateLimiter(max_requests=3, window_seconds=60.0)
        assert rl.allow("ip1") is True
        assert rl.allow("ip1") is True
        assert rl.allow("ip1") is True
        assert rl.allow("ip1") is False

    def test_independent_identifiers(self):
        """Different identifiers have independent rate limits."""
        rl = RateLimiter(max_requests=1, window_seconds=60.0)
        assert rl.allow("a") is True
        assert rl.allow("b") is True
        assert rl.allow("a") is False
        assert rl.allow("b") is False

    def test_remaining_decreases(self):
        """remaining() counts down as requests are consumed."""
        rl = RateLimiter(max_requests=5, window_seconds=60.0)
        assert rl.remaining("ip1") == 5
        rl.allow("ip1")
        assert rl.remaining("ip1") == 4
        rl.allow("ip1")
        assert rl.remaining("ip1") == 3

    def test_remaining_at_zero(self):
        """remaining() returns 0 when limit is exhausted."""
        rl = RateLimiter(max_requests=2, window_seconds=60.0)
        rl.allow("ip1")
        rl.allow("ip1")
        assert rl.remaining("ip1") == 0

    def test_reset_clears_state(self):
        """reset() clears all tracked requests for an identifier."""
        rl = RateLimiter(max_requests=2, window_seconds=60.0)
        rl.allow("ip1")
        rl.allow("ip1")
        assert rl.allow("ip1") is False
        rl.reset("ip1")
        assert rl.allow("ip1") is True
        assert rl.remaining("ip1") == 1

    def test_reset_nonexistent_no_error(self):
        """Resetting an unknown identifier is a no-op."""
        rl = RateLimiter(max_requests=5, window_seconds=60.0)
        rl.reset("ghost")  # Should not raise

    def test_window_expiry(self):
        """Requests outside the window are evicted, freeing capacity."""
        rl = RateLimiter(max_requests=2, window_seconds=0.05)
        rl.allow("ip1")
        rl.allow("ip1")
        assert rl.allow("ip1") is False
        time.sleep(0.06)
        assert rl.allow("ip1") is True

    def test_default_parameters(self):
        """Default constructor: 60 requests / 60 seconds."""
        rl = RateLimiter()
        assert rl.max_requests == 60
        assert rl.window_seconds == 60.0


# ---------------------------------------------------------------------------
# DetectionRule dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDetectionRule:
    """Tests for the DetectionRule dataclass."""

    def test_creation(self):
        """DetectionRule stores all fields correctly."""
        rule = DetectionRule(
            name="sqli",
            category="injection",
            severity=Severity.HIGH,
            check=lambda req: "DROP" in req.get("q", ""),
            description="SQL injection attempt",
            response=ResponseAction.BLOCK,
        )
        assert rule.name == "sqli"
        assert rule.category == "injection"
        assert rule.severity == Severity.HIGH
        assert rule.description == "SQL injection attempt"
        assert rule.response == ResponseAction.BLOCK

    def test_defaults(self):
        """Default description is empty, default response is LOG."""
        rule = DetectionRule(
            name="r", category="c", severity=Severity.INFO, check=lambda _: False
        )
        assert rule.description == ""
        assert rule.response == ResponseAction.LOG


# ---------------------------------------------------------------------------
# ThreatDetector
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestThreatDetector:
    """Tests for the ThreatDetector rule engine."""

    def setup_method(self):
        self.detector = ThreatDetector()

    def test_no_rules_no_threats(self):
        """With no rules, evaluation returns empty list."""
        result = self.detector.evaluate({"path": "/api"})
        assert result == []

    def test_rule_triggers(self):
        """A matching rule generates a ThreatEvent."""
        self.detector.add_rule(
            DetectionRule(
                name="sqli",
                category="injection",
                severity=Severity.HIGH,
                check=lambda req: "DROP TABLE" in req.get("query", "").upper(),
                response=ResponseAction.BLOCK,
            )
        )
        threats = self.detector.evaluate({"query": "DROP TABLE users"}, source="ip1")
        assert len(threats) == 1
        assert threats[0].category == "injection"
        assert threats[0].source == "ip1"
        assert threats[0].severity == Severity.HIGH
        assert threats[0].response == ResponseAction.BLOCK

    def test_rule_does_not_trigger(self):
        """A non-matching rule produces no threats."""
        self.detector.add_rule(
            DetectionRule(
                name="sqli",
                category="injection",
                severity=Severity.HIGH,
                check=lambda req: "DROP TABLE" in req.get("query", ""),
            )
        )
        threats = self.detector.evaluate({"query": "SELECT 1"})
        assert threats == []

    def test_multiple_rules_multiple_triggers(self):
        """Multiple rules can each generate independent threat events."""
        self.detector.add_rule(
            DetectionRule(
                name="r1", category="c1", severity=Severity.LOW, check=lambda _: True
            )
        )
        self.detector.add_rule(
            DetectionRule(
                name="r2", category="c2", severity=Severity.MEDIUM, check=lambda _: True
            )
        )
        threats = self.detector.evaluate({})
        assert len(threats) == 2

    def test_rule_exception_handled(self):
        """A rule that raises an exception is caught; other rules still fire."""
        self.detector.add_rule(
            DetectionRule(
                name="bad",
                category="error",
                severity=Severity.INFO,
                check=lambda _: 1 / 0,  # ZeroDivisionError
            )
        )
        self.detector.add_rule(
            DetectionRule(
                name="good",
                category="ok",
                severity=Severity.LOW,
                check=lambda _: True,
            )
        )
        threats = self.detector.evaluate({})
        assert len(threats) == 1
        assert threats[0].category == "ok"

    def test_description_fallback_to_name(self):
        """When description is empty, the event description uses the rule name."""
        self.detector.add_rule(
            DetectionRule(
                name="my_rule",
                category="c",
                severity=Severity.INFO,
                check=lambda _: True,
            )
        )
        threats = self.detector.evaluate({})
        assert threats[0].description == "my_rule"

    def test_default_source(self):
        """Default source is 'unknown' when not specified."""
        self.detector.add_rule(
            DetectionRule(
                name="r", category="c", severity=Severity.INFO, check=lambda _: True
            )
        )
        threats = self.detector.evaluate({})
        assert threats[0].source == "unknown"


# ---------------------------------------------------------------------------
# Defense orchestrator
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDefense:
    """Tests for the Defense orchestrator: blocklist, rate limiting, detection."""

    def setup_method(self):
        self.defense = Defense()

    # -- Constructor ------------------------------------------------------

    def test_default_init(self):
        """Default construction with empty config."""
        assert self.defense.config == {}
        assert self.defense.limiter.max_requests == 60
        assert self.defense.limiter.window_seconds == 60.0
        assert self.defense.event_log == []
        assert self.defense.blocked_count == 0

    def test_custom_config(self):
        """Custom config controls limiter parameters."""
        d = Defense(config={"max_requests": 10, "window_seconds": 30.0})
        assert d.limiter.max_requests == 10
        assert d.limiter.window_seconds == 30.0

    # -- Block / unblock --------------------------------------------------

    def test_block_source(self):
        """Blocked source is immediately rejected."""
        self.defense.block_source("bad_ip")
        assert self.defense.blocked_count == 1
        allowed, threats = self.defense.process_request("bad_ip", {})
        assert allowed is False
        assert len(threats) == 1
        assert threats[0].category == "blocked"
        assert threats[0].response == ResponseAction.BLOCK

    def test_unblock_source(self):
        """Unblocked source is allowed again."""
        self.defense.block_source("ip1")
        self.defense.unblock_source("ip1")
        assert self.defense.blocked_count == 0
        allowed, _ = self.defense.process_request("ip1", {})
        assert allowed is True

    def test_unblock_nonexistent(self):
        """Unblocking an unknown source is a no-op."""
        self.defense.unblock_source("ghost")  # Should not raise
        assert self.defense.blocked_count == 0

    # -- Rate limiting in process_request ---------------------------------

    def test_rate_limit_triggers(self):
        """Exceeding rate limit causes denial."""
        d = Defense(config={"max_requests": 2, "window_seconds": 60.0})
        assert d.process_request("ip1", {})[0] is True
        assert d.process_request("ip1", {})[0] is True
        allowed, threats = d.process_request("ip1", {})
        assert allowed is False
        assert threats[0].category == "rate_limit"
        assert threats[0].response == ResponseAction.THROTTLE

    # -- Threat detection in process_request ------------------------------

    def test_threat_detection_block(self):
        """A BLOCK response action in a rule causes the request to be denied."""
        self.defense.add_detection_rule(
            DetectionRule(
                name="sqli",
                category="injection",
                severity=Severity.HIGH,
                check=lambda req: "DROP" in req.get("q", ""),
                response=ResponseAction.BLOCK,
            )
        )
        allowed, threats = self.defense.process_request("ip1", {"q": "DROP users"})
        assert allowed is False
        assert len(threats) == 1

    def test_threat_detection_log_only(self):
        """A LOG-only rule allows the request through but records the threat."""
        self.defense.add_detection_rule(
            DetectionRule(
                name="suspicious",
                category="anomaly",
                severity=Severity.LOW,
                check=lambda _: True,
                response=ResponseAction.LOG,
            )
        )
        allowed, threats = self.defense.process_request("ip1", {})
        assert allowed is True
        assert len(threats) == 1
        assert threats[0].category == "anomaly"

    def test_critical_threat_auto_blocks_source(self):
        """A CRITICAL severity threat auto-blocks the source for future requests."""
        self.defense.add_detection_rule(
            DetectionRule(
                name="critical_attack",
                category="exploit",
                severity=Severity.CRITICAL,
                check=lambda _: True,
                response=ResponseAction.LOG,  # Not BLOCK, but CRITICAL auto-blocks
            )
        )
        # First request: allowed (CRITICAL auto-blocks for *future* but LOG doesn't deny this one)
        allowed, threats = self.defense.process_request("attacker", {})
        assert allowed is True
        assert self.defense.blocked_count == 1
        # Second request: blocked via blocklist
        allowed2, threats2 = self.defense.process_request("attacker", {})
        assert allowed2 is False
        assert threats2[0].category == "blocked"

    def test_critical_with_block_action(self):
        """CRITICAL + BLOCK: request denied AND source auto-blocked."""
        self.defense.add_detection_rule(
            DetectionRule(
                name="critical_block",
                category="exploit",
                severity=Severity.CRITICAL,
                check=lambda _: True,
                response=ResponseAction.BLOCK,
            )
        )
        allowed, _ = self.defense.process_request("attacker", {})
        assert allowed is False
        assert self.defense.blocked_count == 1

    def test_clean_request_allowed(self):
        """A clean request with no matching rules is allowed."""
        self.defense.add_detection_rule(
            DetectionRule(
                name="sqli",
                category="injection",
                severity=Severity.HIGH,
                check=lambda req: "DROP" in req.get("q", ""),
                response=ResponseAction.BLOCK,
            )
        )
        allowed, threats = self.defense.process_request("ip1", {"q": "SELECT 1"})
        assert allowed is True
        assert threats == []

    # -- Event log --------------------------------------------------------

    def test_event_log_accumulates(self):
        """Event log tracks all threats from process_request."""
        self.defense.add_detection_rule(
            DetectionRule(
                name="r", category="c", severity=Severity.LOW, check=lambda _: True
            )
        )
        self.defense.process_request("ip1", {})
        self.defense.process_request("ip2", {})
        assert len(self.defense.event_log) == 2

    def test_event_log_is_copy(self):
        """event_log returns a copy, not the internal list."""
        self.defense.add_detection_rule(
            DetectionRule(
                name="r", category="c", severity=Severity.LOW, check=lambda _: True
            )
        )
        self.defense.process_request("ip1", {})
        log1 = self.defense.event_log
        log2 = self.defense.event_log
        assert log1 is not log2

    # -- Pipeline ordering ------------------------------------------------

    def test_blocklist_checked_before_rate_limit(self):
        """Blocklist is checked before rate limiting is applied."""
        d = Defense(config={"max_requests": 100, "window_seconds": 60.0})
        d.block_source("ip1")
        allowed, threats = d.process_request("ip1", {})
        assert allowed is False
        assert threats[0].category == "blocked"
        # Rate limiter should NOT have consumed a request
        assert d.limiter.remaining("ip1") == 100

    def test_rate_limit_checked_before_detection(self):
        """If rate-limited, detection rules are not evaluated."""
        d = Defense(config={"max_requests": 1, "window_seconds": 60.0})
        rule_called = []
        d.add_detection_rule(
            DetectionRule(
                name="spy",
                category="c",
                severity=Severity.LOW,
                check=lambda _: rule_called.append(1) or False,
            )
        )
        d.process_request("ip1", {})  # Allowed; rule runs
        assert len(rule_called) == 1
        d.process_request("ip1", {})  # Rate-limited; rule should NOT run
        assert len(rule_called) == 1


# ---------------------------------------------------------------------------
# Module-level factory
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCreateDefense:
    """Tests for the create_defense convenience function."""

    def test_returns_defense_instance(self):
        """create_defense returns a Defense."""
        d = create_defense()
        assert isinstance(d, Defense)

    def test_passes_config(self):
        """create_defense forwards the config dict."""
        d = create_defense(config={"max_requests": 5})
        assert d.limiter.max_requests == 5
