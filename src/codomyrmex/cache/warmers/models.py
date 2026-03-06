"""Cache warming models: WarmingStrategy, WarmingConfig, WarmingStats."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class WarmingStrategy(Enum):
    """Cache warming strategies."""

    EAGER = "eager"
    LAZY = "lazy"
    SCHEDULED = "scheduled"
    ADAPTIVE = "adaptive"


@dataclass
class WarmingConfig:
    """Configuration for cache warming."""

    strategy: WarmingStrategy = WarmingStrategy.LAZY
    batch_size: int = 100
    max_workers: int = 4
    refresh_interval_s: float = 300.0
    warmup_timeout_s: float = 60.0
    retry_on_failure: bool = True
    max_retries: int = 3


@dataclass
class WarmingStats:
    """Statistics for a cache warming run."""

    keys_warmed: int = 0
    keys_failed: int = 0
    total_time_ms: float = 0.0
    last_warming: datetime | None = None
    errors: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        total = self.keys_warmed + self.keys_failed
        return self.keys_warmed / total if total > 0 else 1.0
