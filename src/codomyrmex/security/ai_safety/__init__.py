"""
AI Safety Submodule for Codomyrmex Security Module.

Provides AI-specific security capabilities including jailbreak detection,
adversarial containment, prompt injection defense, and AI safety monitoring.

This integrates and extends the capabilities previously in the standalone
defense module.
"""

try:
    from codomyrmex.defense.active import ActiveDefense
    ACTIVE_DEFENSE_AVAILABLE = True
except ImportError:
    ActiveDefense = None
    ACTIVE_DEFENSE_AVAILABLE = False

try:
    from codomyrmex.defense.rabbithole import RabbitHole
    RABBITHOLE_AVAILABLE = True
except ImportError:
    RabbitHole = None
    RABBITHOLE_AVAILABLE = False


class AISafetyMonitor:
    """
    Unified AI safety monitoring that combines jailbreak detection,
    prompt injection defense, and adversarial containment.
    """

    def __init__(self):
        self._defense = ActiveDefense() if ACTIVE_DEFENSE_AVAILABLE else None
        self._rabbithole = RabbitHole() if RABBITHOLE_AVAILABLE else None
        self._incidents: list[dict] = []

    def check_input(self, text: str) -> dict:
        """
        Check an input for potential AI safety violations.

        Returns:
            Dict with 'safe' (bool), 'threats' (list), and 'action' (str).
        """
        threats = []
        action = "allow"

        if self._defense:
            result = self._defense.detect_exploit(text)
            if result.get("detected", False):
                threats.extend(result.get("patterns", []))
                action = "block"

        incident = {
            "input_length": len(text),
            "safe": len(threats) == 0,
            "threats": threats,
            "action": action,
        }

        if threats:
            self._incidents.append(incident)

        return incident

    def get_incident_report(self) -> dict:
        """Get a summary of detected incidents."""
        return {
            "total_incidents": len(self._incidents),
            "incidents": self._incidents[-10:],  # Last 10
        }


__all__ = ["AISafetyMonitor"]

if ACTIVE_DEFENSE_AVAILABLE:
    __all__.append("ActiveDefense")

if RABBITHOLE_AVAILABLE:
    __all__.append("RabbitHole")
