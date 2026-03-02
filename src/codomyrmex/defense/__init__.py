"""Defense Module — Threat Detection, Rate Limiting & Response Engine.

Provides:
- ActiveDefense: core exploit detection and response.
- RabbitHole: attacker engagement/diversion system.
- Defense: main orchestrator combining rate limiting, threat detection, and response.
"""

from .active import ActiveDefense
from .defense import (
    Defense,
    DetectionRule,
    ResponseAction,
    Severity,
    ThreatDetector,
    ThreatEvent,
    create_defense,
)
from .rabbithole import RabbitHole

__all__ = [
    "ActiveDefense",
    "RabbitHole",
    "Defense",
    "DetectionRule",
    "ResponseAction",
    "Severity",
    "ThreatDetector",
    "ThreatEvent",
    "create_defense",
]
