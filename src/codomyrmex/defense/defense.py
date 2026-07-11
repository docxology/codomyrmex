from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from time import time
from typing import Any

from .active import ActiveDefense, RabbitHole, ThreatLevel


class Severity(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResponseAction(Enum):
    LOG = "log"
    THROTTLE = "throttle"
    BLOCK = "block"
    ALERT = "alert"
    QUARANTINE = "quarantine"
    RABBITHOLE = "rabbithole"
    POISON = "poison"


@dataclass
class ThreatEvent:
    source: str
    category: str
    severity: Severity
    description: str
    timestamp: float = field(default_factory=time)
    metadata: dict[str, Any] = field(default_factory=dict)
    response: ResponseAction | None = None


@dataclass
class DetectionRule:
    name: str
    category: str
    severity: Severity
    check: Callable[[dict[str, Any]], bool]
    description: str = ""
    response: ResponseAction = ResponseAction.LOG


class RateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: float = 60.0) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, identifier: str) -> bool:
        now = time()
        queue = self._requests[identifier]
        self._evict_old(queue, now)
        if len(queue) >= self.max_requests:
            return False
        queue.append(now)
        return True

    def remaining(self, identifier: str) -> int:
        now = time()
        queue = self._requests[identifier]
        self._evict_old(queue, now)
        return max(0, self.max_requests - len(queue))

    def reset(self, identifier: str) -> None:
        self._requests.pop(identifier, None)

    def _evict_old(self, queue: deque[float], now: float) -> None:
        cutoff = now - self.window_seconds
        while queue and queue[0] <= cutoff:
            queue.popleft()


class ThreatDetector:
    def __init__(self) -> None:
        self._rules: list[DetectionRule] = []

    def add_rule(self, rule: DetectionRule) -> None:
        self._rules.append(rule)

    def evaluate(
        self, request: dict[str, Any], source: str = "unknown"
    ) -> list[ThreatEvent]:
        threats: list[ThreatEvent] = []
        for rule in self._rules:
            try:
                triggered = rule.check(request)
            except Exception:
                continue
            if triggered:
                threats.append(
                    ThreatEvent(
                        source=source,
                        category=rule.category,
                        severity=rule.severity,
                        description=rule.description or rule.name,
                        response=rule.response,
                    )
                )
        return threats


class Defense:
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = dict(config or {})
        self.limiter = RateLimiter(
            max_requests=int(self.config.get("max_requests", 60)),
            window_seconds=float(self.config.get("window_seconds", 60.0)),
        )
        self.detector = ThreatDetector()
        self.active = ActiveDefense()
        self.rabbithole = RabbitHole()
        self._blocked_sources: set[str] = set()
        self._event_log: list[ThreatEvent] = []

    @property
    def event_log(self) -> list[ThreatEvent]:
        return list(self._event_log)

    @property
    def blocked_count(self) -> int:
        return len(self._blocked_sources)

    def block_source(self, source: str) -> None:
        self._blocked_sources.add(source)

    def unblock_source(self, source: str) -> None:
        self._blocked_sources.discard(source)

    def add_detection_rule(self, rule: DetectionRule) -> None:
        self.detector.add_rule(rule)

    def process_request(
        self, source: str, request: dict[str, Any]
    ) -> tuple[bool, list[ThreatEvent]]:
        if self.rabbithole.is_engaged(source):
            threat = ThreatEvent(
                source=source,
                category="containment",
                severity=Severity.HIGH,
                description="source contained in rabbit hole",
                response=ResponseAction.RABBITHOLE,
            )
            self._event_log.append(threat)
            return False, [threat]

        if source in self._blocked_sources:
            threat = ThreatEvent(
                source=source,
                category="blocked",
                severity=Severity.HIGH,
                description="source is blocked",
                response=ResponseAction.BLOCK,
            )
            self._event_log.append(threat)
            return False, [threat]

        if not self.limiter.allow(source):
            threat = ThreatEvent(
                source=source,
                category="rate_limit",
                severity=Severity.MEDIUM,
                description="rate limit exceeded",
                response=ResponseAction.THROTTLE,
            )
            self._event_log.append(threat)
            return False, [threat]

        threats = self.detector.evaluate(request, source=source)
        cognitive = self._detect_cognitive_threat(source, request)
        if cognitive is not None:
            threats.append(cognitive)

        for threat in threats:
            if threat.severity is Severity.CRITICAL:
                self.block_source(source)
            if threat.response is ResponseAction.RABBITHOLE:
                self.rabbithole.engage(source)

        self._event_log.extend(threats)
        blocked_actions = {
            ResponseAction.BLOCK,
            ResponseAction.QUARANTINE,
            ResponseAction.RABBITHOLE,
        }
        allowed = not any(threat.response in blocked_actions for threat in threats)
        return allowed, threats

    def _detect_cognitive_threat(
        self, source: str, request: dict[str, Any]
    ) -> ThreatEvent | None:
        text = str(request.get("input", "") or request.get("prompt", ""))
        if not text:
            return None
        result = self.active.detect_exploit(text)
        if not result["detected"]:
            return None
        level: ThreatLevel = result["threat_level"]
        severity = {
            ThreatLevel.LOW: Severity.LOW,
            ThreatLevel.MEDIUM: Severity.MEDIUM,
            ThreatLevel.HIGH: Severity.HIGH,
            ThreatLevel.CRITICAL: Severity.CRITICAL,
        }.get(level, Severity.INFO)
        response = (
            ResponseAction.RABBITHOLE
            if level in {ThreatLevel.HIGH, ThreatLevel.CRITICAL}
            else ResponseAction.POISON
        )
        return ThreatEvent(
            source=source,
            category="cognitive_exploit",
            severity=severity,
            description="AI prompt exploit pattern detected",
            metadata={"patterns": list(result["patterns"])},
            response=response,
        )


def create_defense(config: dict[str, Any] | None = None) -> Defense:
    return Defense(config)
