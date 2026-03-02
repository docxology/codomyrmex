"""Defense Module — Threat Detection, Rate Limiting & Response Engine.

Provides:
- ThreatEvent: structured threat record with severity/category/source.
- RateLimiter: sliding-window rate limiter per source IP/identifier.
- ThreatDetector: rule-based anomaly detector with configurable thresholds.
- DefenseEngine: orchestrator that combines detection + response actions.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

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


@dataclass
class ThreatEvent:
    """A detected threat occurrence."""

    source: str
    category: str  # "brute_force", "injection", "rate_limit", "anomaly"
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
        """Initialize this instance."""
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._buckets: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, identifier: str) -> bool:
        """Check if a request from this identifier should be allowed.

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
        """Return remaining requests for this identifier in the current window."""
        now = time.time()
        bucket = self._buckets[identifier]
        cutoff = now - self.window_seconds
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        return max(0, self.max_requests - len(bucket))

    def reset(self, identifier: str) -> None:
        """Clear the rate limit state for an identifier."""
        self._buckets.pop(identifier, None)


# ─── Threat Detector ────────────────────────────────────────────────────


@dataclass
class DetectionRule:
    """A threat detection rule."""

    name: str
    category: str
    severity: Severity
    check: Any  # Callable[[dict], bool]
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
        """Initialize this instance."""
        self._rules: list[DetectionRule] = []

    def add_rule(self, rule: DetectionRule) -> None:
        """Register a detection rule."""
        self._rules.append(rule)

    def evaluate(self, request: dict[str, Any], source: str = "unknown") -> list[ThreatEvent]:
        """Evaluate a request against all rules.

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
        """Initialize this instance."""
        self.config = config or {}
        self.limiter = RateLimiter(
            max_requests=self.config.get("max_requests", 60),
            window_seconds=self.config.get("window_seconds", 60.0),
        )
        self.detector = ThreatDetector()
        self._event_log: list[ThreatEvent] = []
        self._blocked_sources: set[str] = set()
        logger.info("Defense engine initialized")

    def add_detection_rule(self, rule: DetectionRule) -> None:
        """Register a threat detection rule."""
        self.detector.add_rule(rule)

    def block_source(self, source: str) -> None:
        """Permanently block a source."""
        self._blocked_sources.add(source)
        logger.warning("Blocked source: %s", source)

    def unblock_source(self, source: str) -> None:
        """Remove a source from the block list."""
        self._blocked_sources.discard(source)

    def process_request(
        self, source: str, request: dict[str, Any]
    ) -> tuple[bool, list[ThreatEvent]]:
        """Process an incoming request through the defense pipeline.

        Returns:
            (allowed, threats): Whether the request is allowed and any detected threats.
        """
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

        # 3. Threat detection
        threats = self.detector.evaluate(request, source=source)
        self._event_log.extend(threats)

        # Auto-block on CRITICAL threats
        for t in threats:
            if t.severity == Severity.CRITICAL:
                self.block_source(source)
            if t.response == ResponseAction.BLOCK:
                return False, threats

        return True, threats

    @property
    def event_log(self) -> list[ThreatEvent]:
        """event Log ."""
        return list(self._event_log)

    @property
    def blocked_count(self) -> int:
        """blocked Count ."""
        return len(self._blocked_sources)


def create_defense(config: dict[str, Any] | None = None) -> Defense:
    """Create a new Defense instance."""
    return Defense(config)
