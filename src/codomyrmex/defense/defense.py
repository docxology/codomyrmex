"""Defense Module — Threat Detection, Rate Limiting & Response Engine.

Provides:
- ThreatEvent: structured threat record with severity/category/source.
- RateLimiter: sliding-window rate limiter per source IP/identifier.
- ThreatDetector: rule-based anomaly detector with configurable thresholds.
- Defense: orchestrator that combines detection + response actions.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from codomyrmex.logging_monitoring import get_logger

from .active import ActiveDefense, ThreatLevel
from .rabbithole import RabbitHole

logger = get_logger(__name__)


class Severity(Enum):
    """Threat severity levels."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResponseAction(Enum):
    """Automated response actions."""

    LOG = "log"
    THROTTLE = "throttle"
    BLOCK = "block"
    ALERT = "alert"
    QUARANTINE = "quarantine"
    RABBITHOLE = "rabbithole"
    POISON = "poison"


@dataclass
class ThreatEvent:
    """A detected threat occurrence."""

    source: str
    category: str  # "brute_force", "injection", "rate_limit", "anomaly", "cognitive_exploit"
    severity: Severity
    description: str
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)
    response: ResponseAction | None = None


# ─── Rate Limiter ───────────────────────────────────────────────────────


class RateLimiter:
    """Sliding-window rate limiter.

    Tracks request counts per identifier within a time window.

    Args:
        max_requests: Maximum requests allowed per window.
        window_seconds: Duration of the sliding window.
    """

    def __init__(self, max_requests: int = 60, window_seconds: float = 60.0) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._buckets: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, identifier: str) -> bool:
        """Check if a request from this identifier should be allowed.

        Args:
            identifier: The unique source identifier (e.g. IP address).

        Returns:
            True if under the rate limit, False if throttled.
        """
        now = time.time()
        bucket = self._buckets[identifier]

        # Evict expired entries
        cutoff = now - self.window_seconds
        while bucket and bucket[0] < cutoff:
            bucket.popleft()

        if len(bucket) >= self.max_requests:
            return False

        bucket.append(now)
        return True

    def remaining(self, identifier: str) -> int:
        """Return remaining requests for this identifier in the current window.

        Args:
            identifier: The unique source identifier.

        Returns:
            Number of remaining requests allowed.
        """
        now = time.time()
        bucket = self._buckets[identifier]
        cutoff = now - self.window_seconds
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        return max(0, self.max_requests - len(bucket))

    def reset(self, identifier: str) -> None:
        """Clear the rate limit state for an identifier.

        Args:
            identifier: The unique source identifier.
        """
        self._buckets.pop(identifier, None)


# ─── Threat Detector ────────────────────────────────────────────────────


@dataclass
class DetectionRule:
    """A threat detection rule."""

    name: str
    category: str
    severity: Severity
    check: Callable[[dict[str, Any]], bool]
    description: str = ""
    response: ResponseAction = ResponseAction.LOG


class ThreatDetector:
    """Rule-based threat detection engine.

    Register rules and evaluate incoming events/requests against them.

    Example::

        detector = ThreatDetector()
        detector.add_rule(DetectionRule(
            name="sql_injection",
            category="injection",
            severity=Severity.HIGH,
            check=lambda req: "DROP TABLE" in req.get("query", "").upper(),
            response=ResponseAction.BLOCK,
        ))
    """

    def __init__(self) -> None:
        self._rules: list[DetectionRule] = []

    def add_rule(self, rule: DetectionRule) -> None:
        """Register a detection rule.

        Args:
            rule: The DetectionRule to add.
        """
        self._rules.append(rule)

    def evaluate(self, request: dict[str, Any], source: str = "unknown") -> list[ThreatEvent]:
        """Evaluate a request against all rules.

        Args:
            request: The request payload to evaluate.
            source: The source identifier.

        Returns:
            List of ThreatEvent for each triggered rule.
        """
        threats: list[ThreatEvent] = []
        for rule in self._rules:
            try:
                if rule.check(request):
                    event = ThreatEvent(
                        source=source,
                        category=rule.category,
                        severity=rule.severity,
                        description=rule.description or rule.name,
                        response=rule.response,
                    )
                    threats.append(event)
            except Exception:
                logger.exception("Detection rule '%s' raised exception", rule.name)
        return threats


# ─── Defense Engine (orchestrator) ──────────────────────────────────────


class Defense:
    """Defense orchestrator combining rate limiting, threat detection, and response.

    Example::

        defense = Defense()
        defense.limiter.max_requests = 10

        # Process an incoming request
        allowed, threats = defense.process_request(
            source="192.168.1.1",
            request={"path": "/api/login", "method": "POST"},
        )
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self.limiter = RateLimiter(
            max_requests=self.config.get("max_requests", 60),
            window_seconds=self.config.get("window_seconds", 60.0),
        )
        self.detector = ThreatDetector()
        self.active_defense = ActiveDefense()
        self.rabbithole = RabbitHole()
        self._event_log: list[ThreatEvent] = []
        self._blocked_sources: set[str] = set()
        logger.info("Defense engine initialized")

    def add_detection_rule(self, rule: DetectionRule) -> None:
        """Register a threat detection rule.

        Args:
            rule: The DetectionRule to add.
        """
        self.detector.add_rule(rule)

    def block_source(self, source: str) -> None:
        """Permanently block a source.

        Args:
            source: The identifier to block.
        """
        self._blocked_sources.add(source)
        logger.warning("Blocked source: %s", source)

    def unblock_source(self, source: str) -> None:
        """Remove a source from the block list.

        Args:
            source: The identifier to unblock.
        """
        self._blocked_sources.discard(source)

    def process_request(
        self, source: str, request: dict[str, Any]
    ) -> tuple[bool, list[ThreatEvent]]:
        """Process an incoming request through the defense pipeline.

        Args:
            source: The unique identifier of the source.
            request: The request data payload.

        Returns:
            A tuple of (allowed, threats) where allowed is True if permitted,
            and threats is a list of detected ThreatEvents.
        """
        # 0. Check if already in Rabbit Hole
        if self.rabbithole.is_engaged(source):
            event = ThreatEvent(
                source=source,
                category="containment",
                severity=Severity.HIGH,
                description="Source is in the rabbit hole",
                response=ResponseAction.RABBITHOLE,
            )
            return False, [event]

        # 1. Check blocklist
        if source in self._blocked_sources:
            event = ThreatEvent(
                source=source,
                category="blocked",
                severity=Severity.HIGH,
                description="Source is on the blocklist",
                response=ResponseAction.BLOCK,
            )
            self._event_log.append(event)
            return False, [event]

        # 2. Rate limiting
        if not self.limiter.allow(source):
            event = ThreatEvent(
                source=source,
                category="rate_limit",
                severity=Severity.MEDIUM,
                description="Rate limit exceeded",
                response=ResponseAction.THROTTLE,
            )
            self._event_log.append(event)
            return False, [event]

        # 3. Rule-based threat detection
        threats = self.detector.evaluate(request, source=source)

        # 4. Cognitive exploit detection (if input is present)
        if "input" in request and isinstance(request["input"], str):
            exploit_result = self.active_defense.detect_exploit(request["input"])
            if exploit_result["detected"]:
                severity_map = {
                    ThreatLevel.NONE: Severity.INFO,
                    ThreatLevel.LOW: Severity.LOW,
                    ThreatLevel.MEDIUM: Severity.MEDIUM,
                    ThreatLevel.HIGH: Severity.HIGH,
                    ThreatLevel.CRITICAL: Severity.CRITICAL,
                }
                event = ThreatEvent(
                    source=source,
                    category="cognitive_exploit",
                    severity=severity_map.get(exploit_result["threat_level"], Severity.MEDIUM),
                    description=f"Cognitive exploit detected: {exploit_result['patterns']}",
                    metadata=exploit_result,
                    response=ResponseAction.RABBITHOLE
                    if exploit_result["threat_level"].value >= ThreatLevel.HIGH.value
                    else ResponseAction.POISON,
                )
                threats.append(event)

        self._event_log.extend(threats)

        # Handle detected threats
        for t in threats:
            if t.severity == Severity.CRITICAL:
                self.block_source(source)

            if t.response == ResponseAction.BLOCK:
                return False, threats

            if t.response == ResponseAction.RABBITHOLE:
                self.rabbithole.engage(source)
                return False, threats

        return True, threats

    @property
    def event_log(self) -> list[ThreatEvent]:
        """Return a copy of the event log."""
        return list(self._event_log)

    @property
    def blocked_count(self) -> int:
        """Return the number of blocked sources."""
        return len(self._blocked_sources)


def create_defense(config: dict[str, Any] | None = None) -> Defense:
    """Create a new Defense instance.

    Args:
        config: Configuration dictionary for the defense system.

    Returns:
        A new initialized Defense instance.
    """
    return Defense(config)
