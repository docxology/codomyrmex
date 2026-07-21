"""Shared palette, loaders, and drawing helpers for manuscript figures."""

from __future__ import annotations

import json
import math
import os
import re
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import yaml
from matplotlib import ticker
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import FancyBboxPatch, RegularPolygon

# ── Palettes ───────────────────────────────────────────────────────────────────

_OI: dict[str, str] = {
    "black": "#000000",
    "orange": "#E69F00",
    "sky": "#56B4E9",
    "green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermil": "#D55E00",
    "pink": "#CC79A7",
    "grey": "#999999",
}

_COVER = {
    "bg": "#060b14",
    "kernel": "#56B4E9",
    "phero": "#E69F00",
    "ledger": "#0072B2",
    "gate": "#D55E00",
    "memory": "#009E73",
    "role": "#CC79A7",
    "prune": "#778899",
    "falsif": "#C8C8D0",
    "spoke": "#1E3A5F",
    "text": "#E8EDF5",
    "dim": "#7A8BA0",
    "grid": "#0A1827",
}

DPI = 300
PROJECT_ROOT = Path(__file__).resolve().parents[4]
FIGDIR = PROJECT_ROOT / "output" / "figures"
VARIABLES_PATH = PROJECT_ROOT / "output" / "data" / "manuscript_variables.json"
CONFIG_PATH = PROJECT_ROOT / "docs" / "manuscript" / "config.yaml"
ROLES_CONFIG_PATH = PROJECT_ROOT / "config" / "colony_kernel" / "roles.yaml"


def _load_json(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(key): str(value) for key, value in data.items()}


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


_VARIABLES = _load_json(VARIABLES_PATH)
_CONFIG = _load_yaml(CONFIG_PATH)
_ROLES_CONFIG = _load_yaml(ROLES_CONFIG_PATH)
_EXPERIMENT = (
    _CONFIG.get("experiment", {})
    if isinstance(_CONFIG.get("experiment", {}), dict)
    else {}
)


def _var_str(name: str, default: str = "") -> str:
    value = _VARIABLES.get(name)
    return value if value not in {None, ""} else default


def _var_float(name: str, default: float) -> float:
    try:
        return float(_VARIABLES.get(name, default))
    except (TypeError, ValueError):
        return default


def _var_list(name: str, default: list[float]) -> list[float]:
    """Decode a generated JSON list token without accepting malformed values."""
    raw = _VARIABLES.get(name)
    if raw:
        try:
            value = json.loads(raw)
            if isinstance(value, list):
                return [float(item) for item in value]
        except (TypeError, ValueError, json.JSONDecodeError):
            pass
    return default


def _experiment_list(key: str, variable_name: str) -> list[float]:
    """Read a list from generated values or the manuscript experiment config."""
    if variable_name in _VARIABLES:
        return _var_list(variable_name, [])
    value = _EXPERIMENT.get(key, [])
    return [float(item) for item in value] if isinstance(value, list) else []


def _experiment_float(key: str, var_name: str, default: float) -> float:
    if var_name in _VARIABLES:
        return _var_float(var_name, default)
    try:
        return float(_EXPERIMENT.get(key, default))
    except (TypeError, ValueError):
        return default


def _gate_weight(name: str, default: float) -> float:
    weights = _EXPERIMENT.get("gate_score_weights", {})
    var_name = f"CONFIG_GATE_WEIGHT_{name.upper()}"
    if var_name in _VARIABLES:
        return _var_float(var_name, default)
    if isinstance(weights, dict):
        try:
            return float(weights.get(name, default))
        except (TypeError, ValueError):
            return default
    return default


def _role_threshold(role_key: str, threshold_key: str, default: float) -> float:
    thresholds = _ROLES_CONFIG.get("thresholds", {})
    if not isinstance(thresholds, dict):
        return default
    role_config = thresholds.get(role_key, {})
    if not isinstance(role_config, dict):
        return default
    try:
        return float(role_config.get(threshold_key, default))
    except (TypeError, ValueError):
        return default


def _role_min_proposals(role_key: str, default: int = 3) -> int:
    thresholds = _ROLES_CONFIG.get("thresholds", {})
    if not isinstance(thresholds, dict):
        return default
    role_config = thresholds.get(role_key, {})
    if not isinstance(role_config, dict):
        return default
    try:
        return int(role_config.get("min_total_proposals", default))
    except (TypeError, ValueError):
        return default


def _figure_parameter(
    key: str,
    variable_name: str,
    default: Any,
    converter: type[Any] = float,
) -> Any:
    """Read a presentation parameter from the generated snapshot/configuration."""
    if variable_name in _VARIABLES:
        try:
            return converter(_VARIABLES[variable_name])
        except (TypeError, ValueError):
            pass
    parameters = _EXPERIMENT.get("figure_parameters", {})
    if isinstance(parameters, dict) and key in parameters:
        try:
            return converter(parameters[key])
        except (TypeError, ValueError):
            pass
    return default


def _figure_parameter_list(key: str, variable_name: str) -> list[float]:
    """Read a configured numeric list, preferring the generated snapshot."""
    raw = _VARIABLES.get(variable_name)
    if raw:
        try:
            value = json.loads(raw)
            if isinstance(value, list):
                return [float(item) for item in value]
        except (TypeError, ValueError, json.JSONDecodeError):
            pass
    parameters = _EXPERIMENT.get("figure_parameters", {})
    value = parameters.get(key, []) if isinstance(parameters, dict) else []
    return [float(item) for item in value] if isinstance(value, list) else []


def _figure_metadata(filename: str) -> dict[str, str]:
    """Return one configured figure record with its caption tokens resolved."""
    figures = _CONFIG.get("figures", {})
    if not isinstance(figures, dict):
        return {}
    for spec in figures.values():
        if not isinstance(spec, dict) or spec.get("filename") != filename:
            continue
        metadata = {str(key): str(value) for key, value in spec.items()}
        token_pattern = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
        metadata["caption"] = token_pattern.sub(
            lambda match: _VARIABLES.get(match.group(1), match.group(0)),
            metadata.get("caption", ""),
        )
        return metadata
    return {}


def _falsification_severity_map() -> dict[str, str]:
    """Return generated vector severities, with a live-source fallback."""
    encoded = _var_str("CONFIG_FALSIFICATION_VECTOR_SEVERITIES")
    if encoded:
        return {
            name: severity
            for item in encoded.split(";")
            if "=" in item
            for name, severity in [item.split("=", 1)]
        }

    from codomyrmex.colony_kernel.falsification.models import (
        _SEVERITY_RANK,
        AttackVector,
    )
    from codomyrmex.colony_kernel.models import FalsificationSeverity

    checks_dir = PROJECT_ROOT / "src/codomyrmex/colony_kernel/falsification/checks"
    rank_to_name = {rank: severity.name for severity, rank in _SEVERITY_RANK.items()}
    values: dict[str, int] = {}
    for path in checks_dir.glob("*.py"):
        source = path.read_text(encoding="utf-8", errors="replace")
        for vector in AttackVector:
            matches = re.findall(
                rf"AttackVector\.{vector.name}\.value.{{0,220}}?"
                r"FalsificationSeverity\.([A-Z]+)",
                source,
                flags=re.DOTALL,
            )
            for severity_name in matches:
                severity = FalsificationSeverity[severity_name]
                values[vector.name] = max(
                    values.get(vector.name, 0), _SEVERITY_RANK[severity]
                )
    return {name: rank_to_name[rank] for name, rank in values.items()}


def _figure_provenance() -> str:
    version = _var_str(
        "CONFIG_VERSION", str(_CONFIG.get("paper", {}).get("version", "unknown"))
    )
    config_hash = _var_str("CONFIG_HASH", "unhashed")
    generated = _var_str("GENERATION_TIMESTAMP", "not regenerated")
    if "T" in generated:
        generated = generated.split("T", 1)[0]
    return f"Codomyrmex v{version} | config {config_hash} | generated {generated}"


def _add_provenance_note(fig: plt.Figure, *, color: str = "#5F6C7B") -> None:
    fig.text(
        0.99,
        0.012,
        _figure_provenance(),
        ha="right",
        va="bottom",
        fontsize=6.4,
        color=color,
    )


def _save(fig: plt.Figure, name: str) -> None:
    FIGDIR.mkdir(parents=True, exist_ok=True)
    dest = FIGDIR / name
    fig.savefig(dest, dpi=DPI, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  saved {dest.relative_to(FIGDIR.parent.parent)}")


def _bezier(
    p0: tuple[float, float],
    p2: tuple[float, float],
    curvature: float = 0.25,
    n_pts: int = 120,
) -> tuple[np.ndarray, np.ndarray]:
    mid = ((p0[0] + p2[0]) / 2, (p0[1] + p2[1]) / 2)
    dx, dy = p2[0] - p0[0], p2[1] - p0[1]
    length = math.sqrt(dx**2 + dy**2) or 1.0
    p1 = (mid[0] - dy / length * curvature, mid[1] + dx / length * curvature)
    t = np.linspace(0, 1, n_pts)
    bx = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t**2 * p2[0]
    by = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t**2 * p2[1]
    return bx, by


def _glow(
    ax: plt.Axes,
    cx: float,
    cy: float,
    color: str,
    r_core: float = 0.12,
    r_max: float = 0.45,
    n_rings: int = 12,
    alpha_peak: float = 0.14,
    zorder: int = 5,
) -> None:
    for k in range(n_rings, 0, -1):
        frac = k / n_rings
        r = r_core + (r_max - r_core) * frac
        alpha = alpha_peak * (1 - frac) ** 0.7
        ax.add_patch(plt.Circle((cx, cy), r, color=color, alpha=alpha, zorder=zorder))
    ax.add_patch(
        plt.Circle((cx, cy), r_core, color=color, alpha=0.96, zorder=zorder + 1)
    )


def _pub_style(ax: plt.Axes) -> None:
    """Clean publication style: hide top/right spines, soft grid."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CCCCCC")
    ax.spines["bottom"].set_color("#CCCCCC")
    ax.tick_params(labelsize=9.5, color="#888888", length=4)
    ax.grid(True, alpha=0.18, linestyle="--", color="#BBBBBB", linewidth=0.7)


# Star-imported by per-figure modules (private helpers are listed explicitly).
__all__ = [
    "DPI",
    "FIGDIR",
    "_COVER",
    "_EXPERIMENT",
    "_OI",
    "BoundaryNorm",
    "FancyBboxPatch",
    "ListedColormap",
    "RegularPolygon",
    "_add_provenance_note",
    "_bezier",
    "_experiment_float",
    "_experiment_list",
    "_falsification_severity_map",
    "_figure_metadata",
    "_figure_parameter",
    "_figure_parameter_list",
    "_figure_provenance",
    "_gate_weight",
    "_glow",
    "_pub_style",
    "_role_min_proposals",
    "_role_threshold",
    "_save",
    "_var_float",
    "_var_list",
    "_var_str",
    "math",
    "mpatches",
    "np",
    "plt",
    "ticker",
    "yaml",
]
