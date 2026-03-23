"""Per-call cost attribution hooks for cloud provider operations.

Provides a decorator and context manager that automatically records
cost entries via :class:`CostTracker` whenever a provider method is
invoked.  Integrates with the telemetry ``Tracer`` to correlate
cost events with execution spans.

Example::

    tracker = CostTracker()
    pricing = ModelPricingTable()
    pricing.set_price("gpt-4o", input_per_1k=0.005, output_per_1k=0.015)

    auto = AutoCostTracker(tracker, pricing)


    @cost_tracked(auto, provider="openai", model="gpt-4o")
    def call_llm(prompt: str) -> str: ...
"""

from __future__ import annotations

import functools
import logging
import threading
import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, runtime_checkable

from .models import CostCategory

if TYPE_CHECKING:
    from .tracker import CostTracker

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


@dataclass(frozen=True)
class ModelPrice:
    """Pricing for a specific model.

    Attributes:
        model_name: Model identifier (e.g. ``"gpt-4o"``).
        input_cost_per_1k_tokens: Cost per 1,000 input tokens in USD.
        output_cost_per_1k_tokens: Cost per 1,000 output tokens in USD.
        cost_per_call: Flat per-call cost (if applicable).
        cost_per_second: Per-second cost (for compute/streaming).
    """

    model_name: str
    input_cost_per_1k_tokens: float = 0.0
    output_cost_per_1k_tokens: float = 0.0
    cost_per_call: float = 0.0
    cost_per_second: float = 0.0


class ModelPricingTable:
    """Lookup table for model-level pricing.

    Thread-safe.  Pre-populated with a few common models.

    Example::

        table = ModelPricingTable()
        table.set_price("gpt-4o", input_per_1k=0.005, output_per_1k=0.015)

        price = table.get_price("gpt-4o")
        total = (input_tokens / 1000) * price.input_cost_per_1k_tokens
    """

    def __init__(self) -> None:
        self._prices: dict[str, ModelPrice] = {}
        self._lock = threading.Lock()

        # Seed with well-known defaults
        self._seed_defaults()

    def set_price(
        self,
        model_name: str,
        *,
        input_per_1k: float = 0.0,
        output_per_1k: float = 0.0,
        per_call: float = 0.0,
        per_second: float = 0.0,
    ) -> None:
        """set pricing for *model_name*.

        Args:
            model_name: Model identifier.
            input_per_1k: Cost per 1 k input tokens (USD).
            output_per_1k: Cost per 1 k output tokens (USD).
            per_call: Flat per-call cost (USD).
            per_second: Cost per second of compute (USD).
        """
        with self._lock:
            self._prices[model_name] = ModelPrice(
                model_name=model_name,
                input_cost_per_1k_tokens=input_per_1k,
                output_cost_per_1k_tokens=output_per_1k,
                cost_per_call=per_call,
                cost_per_second=per_second,
            )

    def get_price(self, model_name: str) -> ModelPrice | None:
        """Retrieve pricing for *model_name*, or ``None`` if unknown."""
        with self._lock:
            return self._prices.get(model_name)

    def list_models(self) -> list[str]:
        """Return all known model names."""
        with self._lock:
            return list(self._prices.keys())

    def calculate_cost(
        self,
        model_name: str,
        *,
        input_tokens: int = 0,
        output_tokens: int = 0,
        duration_seconds: float = 0.0,
        calls: int = 1,
    ) -> float:
        """Calculate the total cost for a usage event.

        Args:
            model_name: Model identifier.
            input_tokens: Number of input tokens consumed.
            output_tokens: Number of output tokens generated.
            duration_seconds: Duration of compute (for per-second pricing).
            calls: Number of calls (for per-call pricing).

        Returns:
            Total estimated cost in USD, or ``0.0`` if model is unknown.
        """
        price = self.get_price(model_name)
        if price is None:
            return 0.0

        total = 0.0
        total += (input_tokens / 1000.0) * price.input_cost_per_1k_tokens
        total += (output_tokens / 1000.0) * price.output_cost_per_1k_tokens
        total += duration_seconds * price.cost_per_second
        total += calls * price.cost_per_call
        return total

    def _seed_defaults(self) -> None:
        """Populate a few well-known model prices."""
        defaults = [
            ("gpt-4o", 0.005, 0.015),
            ("gpt-4o-mini", 0.00015, 0.0006),
            ("gpt-4-turbo", 0.01, 0.03),
            ("claude-3-5-sonnet", 0.003, 0.015),
            ("claude-3-5-haiku", 0.0008, 0.004),
            ("gemini-2.0-flash", 0.0001, 0.0004),
            ("hermes3", 0.0, 0.0),  # local Ollama — free
            ("llava", 0.0, 0.0),  # local Ollama — free
        ]
        for name, inp, out in defaults:
            self._prices[name] = ModelPrice(
                model_name=name,
                input_cost_per_1k_tokens=inp,
                output_cost_per_1k_tokens=out,
            )


@runtime_checkable
class CostHook(Protocol):
    """Protocol for cost event listeners."""

    def on_call_start(self, provider: str, operation: str) -> None:
        """Called before a provider operation begins."""
        ...

    def on_call_end(
        self,
        provider: str,
        operation: str,
        duration_ms: float,
        tokens_used: int,
        cost_usd: float,
    ) -> None:
        """Called after a provider operation completes."""
        ...


class AutoCostTracker:
    """Wraps :class:`CostTracker` for automatic per-call recording.

    Args:
        tracker: The :class:`CostTracker` to record cost entries in.
        pricing: Model pricing table for cost calculation.
        hooks: Optional list of external hooks to notify.

    Example::

        auto = AutoCostTracker(CostTracker(), ModelPricingTable())

        with auto.track("openai", "chat.completion", model="gpt-4o") as ctx:
            result = call_openai(prompt)
            ctx.set_tokens(input=100, output=50)
    """

    def __init__(
        self,
        tracker: CostTracker,
        pricing: ModelPricingTable | None = None,
        hooks: list[CostHook] | None = None,
    ) -> None:
        self._tracker = tracker
        self._pricing = pricing or ModelPricingTable()
        self._hooks: list[CostHook] = hooks or []
        self._lock = threading.Lock()

    @property
    def tracker(self) -> CostTracker:
        """Return the underlying :class:`CostTracker`."""
        return self._tracker

    @property
    def pricing(self) -> ModelPricingTable:
        """Return the pricing table."""
        return self._pricing

    @contextmanager
    def track(
        self,
        provider: str,
        operation: str,
        *,
        model: str = "",
        category: CostCategory = CostCategory.LLM_INFERENCE,
        tags: dict[str, str] | None = None,
    ) -> Generator[_TrackingContext, None, None]:
        """Context manager that records a cost entry on exit.

        Args:
            provider: Provider name.
            operation: Operation name.
            model: Model identifier for pricing lookup.
            category: Cost category.
            tags: Optional metadata tags.

        Yields:
            A :class:`_TrackingContext` where the caller can set token counts.
        """
        ctx = _TrackingContext(model=model)

        for hook in self._hooks:
            try:
                hook.on_call_start(provider, operation)
            except Exception as _exc:
                logger.debug("Hook on_call_start failed", exc_info=True)

        start = time.monotonic()
        try:
            yield ctx
        finally:
            duration_ms = (time.monotonic() - start) * 1000.0
            total_tokens = ctx.input_tokens + ctx.output_tokens

            cost = self._pricing.calculate_cost(
                model or provider,
                input_tokens=ctx.input_tokens,
                output_tokens=ctx.output_tokens,
                duration_seconds=duration_ms / 1000.0,
            )

            merged_tags = {"provider": provider, "operation": operation}
            if model:
                merged_tags["model"] = model
            if tags:
                merged_tags.update(tags)

            self._tracker.record(
                amount=cost,
                category=category,
                description=f"{provider}/{operation}",
                resource_id=model or provider,
                tags=merged_tags,
                metadata={
                    "input_tokens": ctx.input_tokens,
                    "output_tokens": ctx.output_tokens,
                    "duration_ms": round(duration_ms, 2),
                },
            )

            for hook in self._hooks:
                try:
                    hook.on_call_end(
                        provider, operation, duration_ms, total_tokens, cost
                    )
                except Exception as _exc:
                    logger.debug("Hook on_call_end failed", exc_info=True)


class _TrackingContext:
    """Mutable context yielded by :meth:`AutoCostTracker.track`.

    The caller uses :meth:`set_tokens` to report token consumption
    before the context manager exits and records the cost.
    """

    def __init__(self, model: str = "") -> None:
        self.model = model
        self.input_tokens: int = 0
        self.output_tokens: int = 0
        self.metadata: dict[str, Any] = {}

    def set_tokens(self, *, input: int = 0, output: int = 0) -> None:
        """set token counts for cost calculation.

        Args:
            input: Number of input tokens.
            output: Number of output tokens.
        """
        self.input_tokens = input
        self.output_tokens = output


def cost_tracked(
    auto_tracker: AutoCostTracker,
    *,
    provider: str = "unknown",
    operation: str = "",
    model: str = "",
    category: CostCategory = CostCategory.LLM_INFERENCE,
) -> Callable[[F], F]:
    """Decorator that auto-records cost for each invocation.

    The decorated function's cost is based on duration and the ``model``
    pricing.  For token-level cost tracking, use the
    :meth:`AutoCostTracker.track` context manager directly.

    Args:
        auto_tracker: The :class:`AutoCostTracker` instance.
        provider: Provider name.
        operation: Operation label (defaults to function name).
        model: Model identifier for pricing lookup.
        category: Cost category.

    Returns:
        Decorated callable.
    """

    def decorator(fn: F) -> F:
        op = operation or fn.__name__

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with auto_tracker.track(provider, op, model=model, category=category):
                return fn(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


__all__ = [
    "AutoCostTracker",
    "CostHook",
    "ModelPrice",
    "ModelPricingTable",
    "cost_tracked",
]
