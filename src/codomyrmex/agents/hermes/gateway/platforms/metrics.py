"""Platform Adapter base classes and latency metrics tracking."""

import contextlib
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class PlatformMetrics:
    """Tracking latency splits across gateway hops."""

    platform_received_at: float = field(default_factory=time.time)
    inference_started_at: float = 0.0
    inference_completed_at: float = 0.0
    platform_replied_at: float = 0.0

    @property
    def total_latency_ms(self) -> float:
        """Total turnaround time in milliseconds."""
        if self.platform_replied_at == 0.0:
            return 0.0
        return (self.platform_replied_at - self.platform_received_at) * 1000.0

    @property
    def platform_io_latency_ms(self) -> float:
        """Time taken by gateway routing minus inference time."""
        if self.platform_replied_at == 0.0 or self.inference_completed_at == 0.0:
            return 0.0
        total = self.platform_replied_at - self.platform_received_at
        inference = self.inference_completed_at - self.inference_started_at
        return (total - inference) * 1000.0

    @property
    def llm_inference_latency_ms(self) -> float:
        """Time taken entirely by active LLM generation."""
        if self.inference_completed_at == 0.0:
            return 0.0
        return (self.inference_completed_at - self.inference_started_at) * 1000.0

    def to_dict(self) -> dict[str, float]:
        """Convert metrics to dictionary for attachments."""
        return {
            "total_latency_ms": round(self.total_latency_ms, 2),
            "platform_io_latency_ms": round(self.platform_io_latency_ms, 2),
            "llm_inference_latency_ms": round(self.llm_inference_latency_ms, 2),
        }


class PlatformContext:
    """Context tracking wrapper passed through the Hermes gateway router."""

    def __init__(self, platform_name: str, user_id: str) -> None:
        self.platform_name = platform_name
        self.user_id = user_id
        self.metrics = PlatformMetrics()

    @contextlib.contextmanager
    def measure_inference(self) -> Iterator[None]:
        """Context manager tracking exact LLM generation elapsed time."""
        self.metrics.inference_started_at = time.time()
        try:
            yield
        finally:
            self.metrics.inference_completed_at = time.time()

    def finalize(self) -> None:
        """Mark the final reply timestamp."""
        self.metrics.platform_replied_at = time.time()


@runtime_checkable
class GatewayAdapter(Protocol):
    """Protocol for platform-specific Hermes gateways (Telegram, Discord, etc.)."""

    @property
    def platform_name(self) -> str:
        """Name of the platform, e.g., 'telegram'."""
        ...

    async def start(self) -> None:
        """Initialize adapter connection."""
        ...

    async def stop(self) -> None:
        """Teardown adapter connection."""
        ...
