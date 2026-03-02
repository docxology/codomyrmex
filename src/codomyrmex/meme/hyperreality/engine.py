"""HyperrealityEngine — orchestrator for simulation management."""

from __future__ import annotations

from codomyrmex.meme.hyperreality.models import (
    RealityTunnel,
    Simulacrum,
    SimulationLevel,
)
from codomyrmex.meme.hyperreality.simulation import (
    generate_simulacrum,
)


class HyperrealityEngine:
    """Engine for managing hyperreal states and reality tunnels."""

    def __init__(self) -> None:
        self.tunnels: dict[str, RealityTunnel] = {}

    def create_tunnel(self, name: str, filters: list[str]) -> RealityTunnel:
        """Construct a new reality tunnel."""
        tunnel = RealityTunnel(name=name, filters=filters)
        self.tunnels[name] = tunnel
        return tunnel

    def get_tunnel(self, name: str) -> RealityTunnel | None:
        """Retrieve a reality tunnel by name."""
        return self.tunnels.get(name)

    def inject_simulacrum(
        self, tunnel_name: str, referent: str, level: SimulationLevel
    ) -> Simulacrum:
        """Inject a simulacrum into a specific reality tunnel."""
        if tunnel_name not in self.tunnels:
            # Auto-create if not exists for convenience
            self.create_tunnel(tunnel_name, filters=["default"])

        sim = generate_simulacrum(referent, level)
        tunnel = self.tunnels[tunnel_name]
        tunnel.active_simulacra.append(sim)

        # Increase distortion of the tunnel
        tunnel.distortion = min(1.0, tunnel.distortion + (0.1 * level))

        return sim
