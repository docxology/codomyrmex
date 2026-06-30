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
          max_llm_calls: 200
          max_runtime_seconds: 1800.0
          max_risk_level: 0.7
          max_human_attention_minutes: 60.0
          max_merge_risk: 0.6
          max_doc_debt: 500.0
          max_security_exposure: 0.4
          period_seconds: 43200.0

        gate:
          score_execute: 0.60
          score_hold: 0.35
    """
    return _load_yaml_file(_resolve_config_dir() / "kernel.yaml")


def load_roles_yaml() -> dict[str, Any]:
    """Read ``roles.yaml`` from the config directory.

    Returns an empty dict when the file is absent or unreadable.

    Example layout of ``roles.yaml``::

        sandbox:
          max_proposals: 0
        repair_ant:
          min_trust: 0.20
        memory_ant:
          min_trust: 0.35
        dispatcher:
          min_trust: 0.50
        guard_ant:
          min_trust: 0.70
        min_proposals_for_promotion: 3
    """
    return _load_yaml_file(_resolve_config_dir() / "roles.yaml")


def load_decay_yaml() -> dict[str, Any]:
    """Read ``decay_rates.yaml`` from the config directory.

    Returns an empty dict when the file is absent or unreadable.

    Example layout of ``decay_rates.yaml``::

        fast: 0.30
        normal: 0.10
        slow: 0.03
        permanent: 0.0
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
        score_execute = gate_cfg.get("score_execute", 0.55)
    """
    data = load_kernel_yaml()
    return data.get("gate", {})


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
