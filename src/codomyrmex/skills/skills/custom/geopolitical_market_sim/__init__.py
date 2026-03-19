"""Geopolitical Market Simulation — Codomyrmex Skill Package.

This package provides a typed Python facade for the PrediHermes Hermes skill
(``nativ3ai/hermes-geopolitical-market-sim``) as a native Codomyrmex skill.

Exports:
    - :class:`~.geopolitical_market_pipeline.GeopoliticalMarketPipeline` — OO pipeline
    - :class:`~.geopolitical_market_pipeline.TopicConfig` — topic config dataclass
    - Free functions: :func:`~.geopolitical_market_pipeline.health`,
      :func:`~.geopolitical_market_pipeline.track_topic`,
      :func:`~.geopolitical_market_pipeline.run_tracked`,
      :func:`~.geopolitical_market_pipeline.plan_tracked`,
      :func:`~.geopolitical_market_pipeline.dashboard`,
      :func:`~.geopolitical_market_pipeline.list_worldosint_modules`,
      :func:`~.geopolitical_market_pipeline.update_topic`

Prerequisites:
    Install the PrediHermes skill::

        ./scripts/install_hermes_skill.sh

    Or manually::

        git clone https://github.com/nativ3ai/hermes-geopolitical-market-sim
        cd hermes-geopolitical-market-sim && ./install.sh

See also:
    ``docs/agents/hermes/predihermes.md``
"""

from .geopolitical_market_pipeline import (
    SKILL_NAME,
    GeopoliticalMarketPipeline,
    TopicConfig,
    dashboard,
    health,
    list_worldosint_modules,
    plan_tracked,
    run_tracked,
    track_topic,
    update_topic,
)

__all__ = [
    "SKILL_NAME",
    "GeopoliticalMarketPipeline",
    "TopicConfig",
    "dashboard",
    "health",
    "list_worldosint_modules",
    "plan_tracked",
    "run_tracked",
    "track_topic",
    "update_topic",
]
