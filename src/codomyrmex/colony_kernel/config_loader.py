"""Colony Kernel config loader — reads YAML files from config/colony_kernel/.

The config directory is resolved in this order:
1. ``CODOMYRMEX_COLONY_CONFIG`` env var (path override)
2. The canonical repo-relative default: ``<repo_root>/config/colony_kernel/``

The three YAML files are:
- ``kernel.yaml``      — top-level kernel settings (budget, gate thresholds, …)
- ``roles.yaml``       — role-specific configuration
- ``decay_rates.yaml`` — pheromone decay-rate settings

All loaders return an empty ``dict`` when the file is missing so that
callers can rely on keyword-argument defaults and the kernel stays
fully functional without a config directory.

PyYAML (``pyyaml``) is a core dependency of codomyrmex, so
``yaml.safe_load`` is always available.  If, for some reason, the
import fails at runtime, each loader falls back to ``{}`` and logs a
warning through the standard Python ``warnings`` module rather than
raising.
"""

from __future__ import annotations

import os
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from codomyrmex.colony_kernel.kernel import ResourceBudget

try:
    import yaml as _yaml  # pyyaml>=6.0.2 is in core deps

    _YAML_AVAILABLE = True
except ImportError:  # pragma: no cover
    _YAML_AVAILABLE = False
    # YAML loading requires pyyaml — install with: uv sync (it is a core dep)

# ---------------------------------------------------------------------------
# Config directory resolution
# ---------------------------------------------------------------------------

# Default: navigate from src/codomyrmex/colony_kernel/ up 5 levels to repo
# root, then descend into config/colony_kernel/.
#   __file__  = …/src/codomyrmex/colony_kernel/config_loader.py
#   .parent   = …/src/codomyrmex/colony_kernel/
#   .parent^2 = …/src/codomyrmex/
#   .parent^3 = …/src/
#   .parent^4 = …/                          (repo root)
#   / "config" / "colony_kernel"
COLONY_KERNEL_CONFIG_DIR: Path = (
    Path(__file__).parent.parent.parent.parent / "config" / "colony_kernel"
)


def _resolve_config_dir() -> Path:
    """Return the effective config directory, honouring the env-var override."""
    env_override = os.environ.get("CODOMYRMEX_COLONY_CONFIG", "").strip()
    if env_override:
        return Path(env_override)
    return COLONY_KERNEL_CONFIG_DIR


# ---------------------------------------------------------------------------
# Internal YAML helper
# ---------------------------------------------------------------------------


def _load_yaml_file(path: Path) -> dict[str, Any]:
    """Load *path* as YAML and return a dict.  Returns ``{}`` on any error."""
    if not path.exists():
        return {}
    if not _YAML_AVAILABLE:  # pragma: no cover
        warnings.warn(
            "pyyaml is not installed; colony_kernel config files will be ignored. "
            "Install it with: uv sync",
            stacklevel=3,
        )
        return {}
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = _yaml.safe_load(fh)
        if data is None:
            return {}
        if not isinstance(data, dict):
            warnings.warn(
                f"Expected a YAML mapping in {path}, got {type(data).__name__}; "
                "ignoring file.",
                stacklevel=3,
            )
            return {}
        return data
    except Exception as exc:
        warnings.warn(
            f"Failed to load colony_kernel config file {path}: {exc}",
            stacklevel=3,
        )
        return {}


# ---------------------------------------------------------------------------
# Public loaders
# ---------------------------------------------------------------------------


def load_kernel_yaml() -> dict[str, Any]:
    """Read ``kernel.yaml`` from the config directory.

    Returns an empty dict when the file is absent or unreadable.

    Example layout of ``kernel.yaml``::

        budget:
          max_llm_calls: 500
          max_runtime_seconds: 3600.0
          max_risk_level: 0.8
          max_human_attention_minutes: 120.0
          max_merge_risk: 0.7
          max_doc_debt: 1000.0
          max_security_exposure: 0.5
          period_seconds: 86400.0

        gate:
          execute_threshold: 0.75
          hold_threshold: 0.50

    The ``gate.execute_threshold`` key maps to the actuation gate's
    ``_GATE_SCORE_EXECUTE`` constant; ``gate.hold_threshold`` maps to
    ``_GATE_SCORE_HOLD``.
    """
    return _load_yaml_file(_resolve_config_dir() / "kernel.yaml")


def load_roles_yaml() -> dict[str, Any]:
    """Read ``roles.yaml`` from the config directory.

    Returns an empty dict when the file is absent or unreadable.

    Example layout of ``roles.yaml``::

        thresholds:
          repair_ant:
            min_trust: 0.20
            min_total_proposals: 3
          memory_ant:
            min_trust: 0.35
            min_total_proposals: 3
          dispatcher:
            min_trust: 0.50
            min_total_proposals: 3
          guard_ant:
            min_trust: 0.70
            min_total_proposals: 3
          sandbox:
            max_trust: 0.30

        defaults:
          new_agent_trust: 0.1
          new_agent_role: sandbox
    """
    return _load_yaml_file(_resolve_config_dir() / "roles.yaml")


def load_decay_yaml() -> dict[str, Any]:
    """Read ``decay_rates.yaml`` from the config directory.

    Returns an empty dict when the file is absent or unreadable.

    Example layout of ``decay_rates.yaml``::

        FAST: 3.0    # multiplier on base evaporation (base rate: 0.1/tick)
        NORMAL: 1.0
        SLOW: 0.2

        # Default decay tier assigned to each signal type
        signal_defaults:
          FAILURE: FAST
          SUCCESS: SLOW
          RISK: FAST
          NEED: NORMAL
          DEPENDENCY: SLOW
          HUMAN_PRIORITY: SLOW
    """
    return _load_yaml_file(_resolve_config_dir() / "decay_rates.yaml")


# ---------------------------------------------------------------------------
# Convenience constructors
# ---------------------------------------------------------------------------


def default_budget_from_yaml() -> ResourceBudget:
    """Load the ``budget`` section of ``kernel.yaml`` and return a ResourceBudget.

    Falls back to ``ResourceBudget()`` (all defaults) when the file is missing
    or the ``budget`` key is absent.

    Importing ``ResourceBudget`` is deferred to break any potential circular
    import between this module and ``kernel.py``.
    """
    # Deferred import to avoid circular dependency at module load time.
    from codomyrmex.colony_kernel.kernel import ResourceBudget

    data = load_kernel_yaml()
    budget_section = data.get("budget", {})

    if not budget_section:
        return ResourceBudget()

    # Only pass keys that ResourceBudget actually accepts; ignore unknown keys.
    valid_fields = {
        "max_llm_calls",
        "max_runtime_seconds",
        "max_risk_level",
        "max_human_attention_minutes",
        "max_merge_risk",
        "max_doc_debt",
        "max_security_exposure",
        "period_seconds",
    }
    kwargs = {k: v for k, v in budget_section.items() if k in valid_fields}

    try:
        return ResourceBudget(**kwargs)
    except (TypeError, ValueError) as exc:
        warnings.warn(
            f"Invalid budget section in kernel.yaml: {exc}. Using defaults.",
            stacklevel=2,
        )
        return ResourceBudget()


def default_gate_config_from_yaml() -> dict[str, Any]:
    """Return the ``gate`` section of ``kernel.yaml``.

    Returns an empty dict when the section is absent so callers can safely
    use ``dict.get`` with their own defaults::

        gate_cfg = default_gate_config_from_yaml()
        execute_threshold = gate_cfg.get("execute_threshold", 0.75)
        hold_threshold = gate_cfg.get("hold_threshold", 0.50)

    The canonical key names in ``kernel.yaml`` are:
      - ``execute_threshold`` (maps to ``_GATE_SCORE_EXECUTE`` in actuation_gate.py)
      - ``hold_threshold``    (maps to ``_GATE_SCORE_HOLD`` in actuation_gate.py)

    Note: Legacy YAML files may use ``score_execute`` / ``score_hold`` as key
    names — those are also accepted but the canonical names are preferred.

    Raises:
        None — all errors fall back to returning ``{}``.
    """
    data = load_kernel_yaml()
    gate_section = data.get("gate", {})

    # Validate gate score weights sum constraints
    if gate_section:
        execute = gate_section.get(
            "execute_threshold", gate_section.get("score_execute")
        )
        hold = gate_section.get("hold_threshold", gate_section.get("score_hold"))
        if execute is not None and hold is not None:
            try:
                execute_f = float(execute)
                hold_f = float(hold)
                if not (0.0 < hold_f < execute_f <= 1.0):
                    warnings.warn(
                        f"kernel.yaml gate thresholds are inconsistent: "
                        f"hold_threshold={hold_f} must be < execute_threshold={execute_f} "
                        f"and both must be in (0.0, 1.0]. Using raw values anyway.",
                        stacklevel=2,
                    )
            except (TypeError, ValueError):
                pass

    return gate_section


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------

__all__ = [
    "COLONY_KERNEL_CONFIG_DIR",
    "default_budget_from_yaml",
    "default_gate_config_from_yaml",
    "load_decay_yaml",
    "load_kernel_yaml",
    "load_roles_yaml",
]
