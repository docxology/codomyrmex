"""Mission Control Agent module for Codomyrmex.

Provides integration with the builderz-labs/mission-control open-source
dashboard for AI agent orchestration. Communicates with the dashboard
via its REST API for agent management, task tracking, cost monitoring,
and real-time workflow orchestration.

See: https://github.com/builderz-labs/mission-control
"""

from codomyrmex.agents.mission_control.mission_control_client import (
    MissionControlClient,
    MissionControlConfig,
    MissionControlError,
)

__all__ = [
    "MissionControlClient",
    "MissionControlConfig",
    "MissionControlError",
]
