"""PheromoneStore — typed colony signal layer over TraceField.

Wraps the agentic_memory stigmergy TraceField to give colony semantics:
each ColonySignal is stored under the compound key
``f"{signal_type.value}:{location}"`` so signals of different types at the
same location remain distinct ledger entries.

Decay rates are realised by constructing per-signal StigmergyConfig instances
whose ``evaporation_per_tick`` matches the DecayRate multiplier applied to the
base rate of 0.1/tick:

  FAST  → base * 3.0 = 0.30 / tick
  NORMAL → base * 1.0 = 0.10 / tick
  SLOW  → base * 0.2 = 0.02 / tick

Because TraceField operates with a single shared evaporation rate, and signals
may need different rates, each deposited signal is managed through a
per-signal-key StigmergyConfig embedded in the marker's metadata — the
``evaporate()`` method reads that per-key rate instead of calling
TraceField.tick() directly.
"""

from __future__ import annotations

import time
from typing import Any

from codomyrmex.agentic_memory.stigmergy.field import TraceField
from codomyrmex.agentic_memory.stigmergy.models import StigmergyConfig, TraceMarker
from codomyrmex.colony_kernel.models import (
    ColonySignal,
    DecayRate,
    SignalSource,
    SignalType,
    make_trace_key,
)
from codomyrmex.colony_kernel.sqlite_signal_store import SQLiteSignalStore

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_BASE_EVAPORATION: float = 0.1

# Maximum allowed deposit strength — guards against runaway reinforcement.
# Deposits exceeding this are clamped with a warning rather than silently allowed
# (or rejected with an exception that would break the pipeline).
_MAX_DEPOSIT_STRENGTH: float = 1_000_000.0  # 1e6

# Maps DecayRate enum value to evaporation_per_tick
# Per-signal-type decay class assignments are documented in
# docs/manuscript/02_methodology.md (Table: Signal types) and
# docs/manuscript/05_experimental_setup.md (Table 3):
#   FAILURE -> FAST, RISK -> FAST, NEED -> NORMAL,
#   SUCCESS -> SLOW, DEPENDENCY -> SLOW, HUMAN_PRIORITY -> SLOW
_DECAY_TO_EVAPORATION: dict[DecayRate, float] = {
    DecayRate.FAST: _BASE_EVAPORATION * DecayRate.FAST.value,  # 0.30
    DecayRate.NORMAL: _BASE_EVAPORATION * DecayRate.NORMAL.value,  # 0.10
    DecayRate.SLOW: _BASE_EVAPORATION * DecayRate.SLOW.value,  # 0.02
}

# Source trust multipliers applied at deposit time.
# HUMAN and TEST signals carry higher credibility than raw AGENT/RUNTIME signals.
_SOURCE_MULTIPLIER: dict = {
    "test": 1.5,
    "human": 2.0,
    "security": 1.5,
    "agent": 1.0,
    "runtime": 1.0,
}

# Metadata keys stored inside each TraceMarker
_META_SIGNAL_TYPE = "signal_type"
_META_DECAY_RATE = "decay_rate"
_META_SOURCE = "source"
_META_LOCATION = "location"
_META_EVIDENCE = "evidence"
_META_LAST_REINFORCED = "last_reinforced"
_META_EVAPORATION = "evaporation_per_tick"


def _make_key(signal_type: SignalType, location: str) -> str:
    """Compound key used in the backing TraceField.

    Delegates to :func:`~codomyrmex.colony_kernel.models.make_trace_key` to
    ensure the canonical ``"{location}:{signal_type.value}"`` ordering (SPEC §1).

    Note: The parameter order here has ``signal_type`` first (matching historical
    call-sites within this module), but the resulting key always places *location*
    first per the SPEC convention.
    """
    return make_trace_key(location, signal_type)


def _marker_to_signal(marker: TraceMarker) -> ColonySignal:
    """Reconstruct a ColonySignal from a TraceMarker's metadata + strength."""
    meta = marker.metadata
    return ColonySignal(
        location=meta[_META_LOCATION],
        signal_type=SignalType(meta[_META_SIGNAL_TYPE]),
        strength=marker.strength,
        decay_rate=DecayRate(meta[_META_DECAY_RATE]),
        source=SignalSource(meta[_META_SOURCE]),
        evidence=dict(meta.get(_META_EVIDENCE, {})),
        last_reinforced=meta.get(_META_LAST_REINFORCED, marker.updated_at),
    )


class PheromoneStore:
    """Colony-level pheromone ledger built on top of TraceField.

    Provides typed deposit/query/reinforcement operations using ColonySignal
    as the external contract.  Internally every signal maps to one TraceMarker
    entry whose ``metadata`` carries the colony fields and the per-signal
    evaporation rate (used by the custom ``evaporate()`` tick).

    Example usage::

        store = PheromoneStore()
        store.deposit_signal(
            ColonySignal(
                location="codomyrmex.git_operations.core",
                signal_type=SignalType.FAILURE,
                strength=3.5,
                decay_rate=DecayRate.FAST,
                source=SignalSource.TEST,
                evidence={"test_id": "test_git_push_fails"},
            )
        )
        signals = store.query_pressure("codomyrmex.git_operations", SignalType.FAILURE)
    """

    def __init__(
        self, config: StigmergyConfig | None = None, db_path: str | None = None
    ) -> None:
        """Initialise with a TraceField and an empty key-rate map.

        Args:
            config: Optional StigmergyConfig to pass to the backing TraceField.
                    evaporation_per_tick is overridden to 0.0 regardless of the
                    supplied config — all evaporation is handled per-signal by
                    PheromoneStore.evaporate().
        """
        # Single shared field; evaporation is handled per-key in our tick.
        # We use evaporation_per_tick=0.0 on the shared config so that
        # TraceField.tick() (if ever called externally) does nothing — all
        # evaporation is owned by PheromoneStore.evaporate().
        if config is None:
            field_config = StigmergyConfig(evaporation_per_tick=0.0)
        else:
            import dataclasses

            field_config = dataclasses.replace(config, evaporation_per_tick=0.0)
        self._field: TraceField = TraceField(field_config)
        # key -> evaporation_per_tick for custom per-signal decay
        self._key_evaporation: dict[str, float] = {}
        # location -> set[key] index for O(|results|) prefix queries instead of O(N).
        # Updated by deposit_signal and evaporate.
        self._location_index: dict[str, set[str]] = {}
        self._persistent = (
            SQLiteSignalStore(db_path, config=field_config) if db_path else None
        )

    # ------------------------------------------------------------------
    # Deposit & reinforce
    # ------------------------------------------------------------------

    def deposit_signal(self, signal: ColonySignal) -> None:
        """Deposit or reinforce a ColonySignal in the pheromone field.

        If a trace already exists for the (signal_type, location) pair its
        strength is incremented by ``signal.strength``; otherwise a fresh
        marker is created.  The per-signal evaporation rate from
        ``signal.decay_rate`` is stored in both ``_key_evaporation`` and the
        marker metadata so that ``evaporate()`` applies the correct rate on
        each tick.

        Args:
            signal: The colony signal to deposit.

        Raises:
            ValueError: If ``signal.strength`` exceeds ``_MAX_DEPOSIT_STRENGTH``
                (1e6) — this guards against accidental or adversarial runaway
                reinforcement that would dominate the field.
        """
        if signal.strength > _MAX_DEPOSIT_STRENGTH:
            import warnings as _warnings
            _warnings.warn(
                f"PheromoneStore.deposit_signal: strength {signal.strength!r} exceeds "
                f"maximum allowed value {_MAX_DEPOSIT_STRENGTH}; clamping to "
                f"{_MAX_DEPOSIT_STRENGTH}.",
                stacklevel=2,
            )
            import dataclasses as _dc
            signal = _dc.replace(signal, strength=_MAX_DEPOSIT_STRENGTH)

        if self._persistent is not None:
            self._persistent.deposit(signal)
            return

        key = _make_key(signal.signal_type, signal.location)
        evaporation = _DECAY_TO_EVAPORATION[signal.decay_rate]
        self._key_evaporation[key] = evaporation

        # Update the location → key index
        loc = signal.location
        if loc not in self._location_index:
            self._location_index[loc] = set()
        self._location_index[loc].add(key)

        metadata: dict[str, Any] = {
            _META_SIGNAL_TYPE: signal.signal_type.value,
            _META_DECAY_RATE: signal.decay_rate.value,
            _META_SOURCE: signal.source.value,
            _META_LOCATION: signal.location,
            _META_EVIDENCE: dict(signal.evidence),
            _META_LAST_REINFORCED: signal.last_reinforced,
            _META_EVAPORATION: evaporation,
        }
        self._field.deposit(key, initial=signal.strength, metadata=metadata)

    def reinforce_path(self, location: str, signal_type: SignalType) -> None:
        """Reinforce an existing signal at *location* for *signal_type*.

        Uses TraceField's built-in reinforce delta (0.15 by default).  If no
        matching trace exists this is a no-op.

        Args:
            location: The dotted module path or file path to reinforce.
            signal_type: Which signal type to strengthen at that location.
        """
        if self._persistent is not None:
            self._persistent.reinforce(location, signal_type)
            return
        key = _make_key(signal_type, location)
        marker = self._field.reinforce(key)
        if marker is not None:
            marker.metadata[_META_LAST_REINFORCED] = time.time()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def query_pressure(
        self,
        location: str,
        signal_type: SignalType | None = None,
    ) -> list[ColonySignal]:
        """Return all signals whose location starts with *location*.

        Performs a prefix match so ``"codomyrmex.git_operations"`` returns
        signals for ``"codomyrmex.git_operations"`` and
        ``"codomyrmex.git_operations.core"`` etc.

        Uses the internal location index for O(|results|) performance instead
        of iterating all markers (O(N)).  Falls back to a full scan if the
        index is stale or missing (defensive path for backward compatibility).

        Args:
            location: Location prefix to match against.
            signal_type: If given, restrict results to this signal type.

        Returns:
            List of matching ColonySignal objects sorted by descending strength.
        """
        if self._persistent is not None:
            signals = self._persistent.all_signals()
            results = [
                signal
                for signal in signals
                if (
                    signal.location == location
                    or signal.location.startswith((location + ".", location + "/"))
                )
                and (signal_type is None or signal.signal_type is signal_type)
            ]
            results.sort(key=lambda s: s.strength, reverse=True)
            return results

        results: list[ColonySignal] = []

        # Collect candidate keys from the location index using prefix matching.
        candidate_keys: set[str] = set()
        for loc_key, key_set in self._location_index.items():
            if loc_key == location or loc_key.startswith(
                (location + ".", location + "/")
            ):
                candidate_keys.update(key_set)

        if candidate_keys:
            # Fast path — use index-backed lookup
            for key in candidate_keys:
                marker = self._field._markers.get(key)
                if marker is None:
                    continue
                meta = marker.metadata
                if signal_type is not None:
                    if meta.get(_META_SIGNAL_TYPE) != signal_type.value:
                        continue
                results.append(_marker_to_signal(marker))
        else:
            # Slow path — full scan (covers edge cases where index may be incomplete)
            all_markers = self._field.top_k(k=len(self._field) or 1)
            for marker in all_markers:
                meta = marker.metadata
                marker_location: str = meta.get(_META_LOCATION, "")
                if not (
                    marker_location == location
                    or marker_location.startswith((location + ".", location + "/"))
                ):
                    continue
                if signal_type is not None:
                    if meta.get(_META_SIGNAL_TYPE) != signal_type.value:
                        continue
                results.append(_marker_to_signal(marker))

        results.sort(key=lambda s: s.strength, reverse=True)
        return results

    def query_by_source(self, source: SignalSource) -> list[ColonySignal]:
        """Return all signals deposited by *source*, sorted by descending strength.

        Args:
            source: The SignalSource to filter by.

        Returns:
            List of ColonySignal objects from that source.
        """
        if self._persistent is not None:
            return [
                signal
                for signal in self._persistent.all_signals()
                if signal.source is source
            ]
        results: list[ColonySignal] = []
        all_markers = self._field.top_k(k=len(self._field) or 1)
        for marker in all_markers:
            if marker.metadata.get(_META_SOURCE) == source.value:
                results.append(_marker_to_signal(marker))
        results.sort(key=lambda s: s.strength, reverse=True)
        return results

    def query_by_signal_type(self, signal_type: SignalType) -> list[ColonySignal]:
        """Return all signals of a given *signal_type*, sorted by descending strength.

        Args:
            signal_type: The SignalType to filter by.

        Returns:
            List of ColonySignal objects of that type.
        """
        if self._persistent is not None:
            return [
                signal
                for signal in self._persistent.all_signals()
                if signal.signal_type is signal_type
            ]
        results: list[ColonySignal] = []
        all_markers = self._field.top_k(k=len(self._field) or 1)
        for marker in all_markers:
            if marker.metadata.get(_META_SIGNAL_TYPE) == signal_type.value:
                results.append(_marker_to_signal(marker))
        results.sort(key=lambda s: s.strength, reverse=True)
        return results

    def top_pressure(self, k: int = 10) -> list[ColonySignal]:
        """Return the *k* strongest signals across the entire field.

        Args:
            k: Number of results to return (default 10).

        Returns:
            List of up to *k* ColonySignal objects in descending strength order.
        """
        if self._persistent is not None:
            return self._persistent.all_signals()[:k]
        markers = self._field.top_k(k=k)
        return [_marker_to_signal(m) for m in markers]

    # ------------------------------------------------------------------
    # Tick / evaporation
    # ------------------------------------------------------------------

    def evaporate(self) -> None:
        """Advance time by one tick, applying per-signal evaporation rates.

        Each trace has its own evaporation_per_tick stored in its metadata
        (set at deposit time from DecayRate).  This method applies those
        individual rates rather than a single global rate, then prunes traces
        whose strength has dropped to or below the field's min_strength (0.0).

        This replaces calling ``TraceField.tick()`` directly — that would use
        the shared config rate of 0.0 set at construction time.
        """
        if self._persistent is not None:
            self._persistent.evaporate()
            return
        min_strength = self._field.config.min_strength
        keys_to_remove: list[str] = []

        # Access internal markers dict to apply per-key decay
        for key, marker in self._field._markers.items():
            evap = self._key_evaporation.get(
                key, marker.metadata.get(_META_EVAPORATION, _BASE_EVAPORATION)
            )
            marker.strength -= evap
            if marker.strength <= min_strength:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self._field._markers[key]
            self._key_evaporation.pop(key, None)
            # Clean up the location index
            # The key format is "{location}:{signal_type}" per make_trace_key.
            # We extract the location by finding the last ":" component.
            loc = key.rsplit(":", 1)[0] if ":" in key else key
            loc_keys = self._location_index.get(loc)
            if loc_keys is not None:
                loc_keys.discard(key)
                if not loc_keys:
                    del self._location_index[loc]

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> dict[str, Any]:
        """Return a diagnostic summary of the current pheromone field state.

        Returns a dict with:
        - ``total_signals``: int — total live traces in the field.
        - ``by_signal_type``: dict[str, int] — count per SignalType value.
        - ``by_source``: dict[str, int] — count per SignalSource value.
        - ``by_decay_rate``: dict[str, int] — count per DecayRate value.
        - ``top_5``: list[dict] — top-5 signals as plain dicts (location,
          signal_type, strength, source, decay_rate).
        - ``max_strength``: float — strength of the strongest live signal.
        - ``min_strength``: float — strength of the weakest live signal.
        - ``mean_strength``: float — mean strength across all live signals.

        Returns:
            Dictionary of summary statistics.
        """
        if self._persistent is not None:
            signals = self._persistent.all_signals()
            by_type: dict[str, int] = {}
            by_source: dict[str, int] = {}
            by_decay: dict[str, int] = {}
            strengths = [signal.strength for signal in signals]
            for signal in signals:
                by_type[signal.signal_type.value] = by_type.get(signal.signal_type.value, 0) + 1
                by_source[signal.source.value] = by_source.get(signal.source.value, 0) + 1
                decay_key = str(signal.decay_rate.value)
                by_decay[decay_key] = by_decay.get(decay_key, 0) + 1
            return {
                "total_signals": len(signals),
                "by_signal_type": by_type,
                "by_source": by_source,
                "by_decay_rate": by_decay,
                "top_5": [
                    {
                        "location": signal.location,
                        "signal_type": signal.signal_type.value,
                        "strength": signal.strength,
                        "source": signal.source.value,
                        "decay_rate": signal.decay_rate.value,
                    }
                    for signal in signals[:5]
                ],
                "max_strength": max(strengths, default=0.0),
                "min_strength": min(strengths, default=0.0),
                "mean_strength": sum(strengths) / len(signals) if signals else 0.0,
            }

        all_markers = self._field.top_k(k=len(self._field) or 1)
        total = len(all_markers)

        by_type: dict[str, int] = {}
        by_source: dict[str, int] = {}
        by_decay: dict[str, int] = {}
        strengths: list[float] = []

        for marker in all_markers:
            meta = marker.metadata
            st = meta.get(_META_SIGNAL_TYPE, "unknown")
            src = meta.get(_META_SOURCE, "unknown")
            dr = meta.get(_META_DECAY_RATE, "unknown")
            by_type[st] = by_type.get(st, 0) + 1
            by_source[src] = by_source.get(src, 0) + 1
            by_decay[dr] = by_decay.get(dr, 0) + 1
            strengths.append(marker.strength)

        top5 = [
            {
                "location": m.metadata.get(_META_LOCATION, ""),
                "signal_type": m.metadata.get(_META_SIGNAL_TYPE, ""),
                "strength": m.strength,
                "source": m.metadata.get(_META_SOURCE, ""),
                "decay_rate": m.metadata.get(_META_DECAY_RATE, ""),
            }
            for m in all_markers[:5]
        ]

        return {
            "total_signals": total,
            "by_signal_type": by_type,
            "by_source": by_source,
            "by_decay_rate": by_decay,
            "top_5": top5,
            "max_strength": max(strengths, default=0.0),
            "min_strength": min(strengths, default=0.0),
            "mean_strength": (sum(strengths) / total) if total > 0 else 0.0,
        }

    # ------------------------------------------------------------------
    # Kernel-compatible aliases
    # ------------------------------------------------------------------

    def deposit(self, signal: ColonySignal, trust_factor: float = 1.0) -> None:
        """Kernel-compatible deposit with source trust multiplier and trust_factor scaling.

        Applies the source trust multiplier (TEST=1.5, HUMAN=2.0, SECURITY=1.5,
        AGENT=1.0, RUNTIME=1.0) then multiplies by ``trust_factor`` before
        delegating to :meth:`deposit_signal`.

        This method is the correct entry-point for colony-kernel callers.
        Tests that want to deposit at exact strength should call
        :meth:`deposit_signal` directly (no multiplier applied there).
        """
        import dataclasses

        multiplier = _SOURCE_MULTIPLIER.get(signal.source.value, 1.0)
        effective = signal.strength * multiplier * trust_factor
        scaled = dataclasses.replace(signal, strength=effective)
        self.deposit_signal(scaled)

    def reinforce(self, location: str, signal_type: SignalType) -> None:
        """Alias for reinforce_path. Kernel-compatible API."""
        self.reinforce_path(location, signal_type)

    def sense(self, location: str, signal_type: SignalType) -> float:
        """Return pheromone strength at (location, signal_type); 0.0 if absent.

        Kernel-compatible API wrapping query_pressure.
        """
        if self._persistent is not None:
            signal = self._persistent.sense(location, signal_type)
            return signal.strength if signal is not None else 0.0
        key = _make_key(signal_type, location)
        marker = self._field.sense(key)
        return marker.strength if marker is not None else 0.0

    def tick(self) -> int:
        """Evaporate all traces using per-signal decay rates; returns removed count.

        Kernel-compatible API wrapping evaporate().
        """
        count_before = len(self._persistent) if self._persistent else len(self._field)
        self.evaporate()
        count_after = len(self._field)
        return max(0, count_before - count_after)

    def top_signals(self, k: int = 10) -> list[dict]:
        """Return the k strongest signals as plain dicts for colony_status.

        Kernel-compatible API wrapping top_pressure().
        """
        signals = self.top_pressure(k=k)
        results = []
        for s in signals:
            key = _make_key(s.signal_type, s.location)
            parts = key.split(":", 1)
            results.append(
                {
                    "key": key,
                    "location": parts[0],
                    "signal_type": parts[1] if len(parts) > 1 else "unknown",
                    "strength": s.strength,
                    "updated_at": s.last_reinforced,
                }
            )
        return results

    def __len__(self) -> int:
        return len(self._persistent) if self._persistent else len(self._field)

    def clear(self) -> int:
        """Clear all signals and return the number removed."""

        if self._persistent is not None:
            return self._persistent.clear()
        count = len(self._field)
        self._field._markers.clear()
        self._key_evaporation.clear()
        self._location_index.clear()
        return count

    def close(self) -> None:
        """Close a durable backend, if configured."""

        if self._persistent is not None:
            self._persistent.close()


__all__ = ["PheromoneStore"]
