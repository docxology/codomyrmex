"""Shared palette, loaders, and drawing helpers for manuscript figures."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any

# Figure generation is a headless artifact pipeline. Force a non-GUI backend so
# macOS window services cannot affect reproducibility or CI execution.
os.environ["MPLBACKEND"] = "Agg"

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


class FigureConfigurationError(RuntimeError):
    """Raised when a figure cannot be tied to the generated manuscript snapshot."""


def _require_variable(name: str) -> str:
    """Return a generated variable or fail closed instead of inventing a value.

    Figure generation is a publication step, so a missing or stale snapshot is a
    correctness error rather than an invitation to use a plausible default.  The
    config digest catches the common case where prose/configuration changed after
    variable generation; the source digest catches kernel changes that would alter
    the derived values while leaving the YAML untouched.
    """
    if not _VARIABLES:
        raise FigureConfigurationError(
            f"Generated manuscript variables are missing: {VARIABLES_PATH}. "
            "Run scripts/z_generate_manuscript_variables.py first."
        )
    config_hash = str(_VARIABLES.get("CONFIG_HASH", "")).replace(" ", "")
    if config_hash != hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest():
        raise FigureConfigurationError(
            "Generated manuscript variables are stale relative to "
            f"{CONFIG_PATH}; regenerate before drawing figures."
        )
    source_hash = str(_VARIABLES.get("REPRO_KERNEL_SOURCE_HASH", "")).replace(" ", "")
    if not source_hash or source_hash != _kernel_source_hash():
        raise FigureConfigurationError(
            "Generated manuscript variables are missing or stale relative to "
            "Colony Kernel source; regenerate before drawing figures."
        )
    value = _VARIABLES.get(name)
    if value in {None, ""}:
        raise FigureConfigurationError(
            f"Generated manuscript variable {name!r} is missing; regenerate the "
            "manuscript variable snapshot."
        )
    return str(value)


def _kernel_source_hash() -> str:
    """Hash the first-party sources used to derive kernel manuscript values."""
    digest = hashlib.sha256()
    source_root = PROJECT_ROOT / "src" / "codomyrmex" / "colony_kernel"
    paths = sorted(source_root.rglob("*.py"))
    paths.append(PROJECT_ROOT / "src" / "codomyrmex" / "manuscript" / "variables.py")
    for path in paths:
        digest.update(str(path.relative_to(PROJECT_ROOT)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _var_str(name: str) -> str:
    return _require_variable(name)


def _var_float(name: str) -> float:
    try:
        return float(_require_variable(name))
    except (TypeError, ValueError) as exc:
        raise FigureConfigurationError(
            f"Generated manuscript variable {name!r} is not numeric"
        ) from exc


def _var_list(name: str) -> list[float]:
    """Decode a generated JSON list token without accepting malformed values."""
    try:
        value = json.loads(_require_variable(name))
        if not isinstance(value, list):
            raise TypeError("expected a JSON list")
        return [float(item) for item in value]
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise FigureConfigurationError(
            f"Generated manuscript variable {name!r} is not a numeric JSON list"
        ) from exc


def _experiment_list(key: str, variable_name: str) -> list[float]:
    """Read a list from the generated snapshot, never directly from config."""
    del key
    return _var_list(variable_name)


def _experiment_float(key: str, var_name: str) -> float:
    del key
    return _var_float(var_name)


def _gate_weight(name: str) -> float:
    var_name = f"CONFIG_GATE_WEIGHT_{name.upper()}"
    return _var_float(var_name)


def _role_threshold(role_key: str, threshold_key: str) -> float:
    del threshold_key
    variable_names = {
        "repair_ant": "CONFIG_ROLE_REPAIR_THRESHOLD",
        "memory_ant": "CONFIG_ROLE_MEMORY_THRESHOLD",
        "dispatcher": "CONFIG_ROLE_DISPATCHER_THRESHOLD",
        "guard_ant": "CONFIG_ROLE_GUARD_THRESHOLD",
    }
    try:
        variable_name = variable_names[role_key]
    except KeyError as exc:
        raise FigureConfigurationError(
            f"No generated role-threshold variable is defined for {role_key!r}"
        ) from exc
    return _var_float(variable_name)


def _role_min_proposals(role_key: str) -> int:
    del role_key
    try:
        return int(_var_float("CONFIG_ROLE_MIN_PROPOSALS"))
    except (TypeError, ValueError) as exc:
        raise FigureConfigurationError(
            "Generated manuscript role proposal threshold is not an integer"
        ) from exc


def _figure_parameter(
    key: str,
    variable_name: str,
    converter: type[Any] = float,
) -> Any:
    """Read a presentation parameter only from the generated snapshot."""
    del key
    try:
        return converter(_require_variable(variable_name))
    except (TypeError, ValueError) as exc:
        raise FigureConfigurationError(
            f"Generated figure variable {variable_name!r} has an invalid value"
        ) from exc


def _figure_parameter_list(key: str, variable_name: str) -> list[float]:
    """Read a configured numeric list only from the generated snapshot."""
    del key
    return _var_list(variable_name)


def _figure_metadata(filename: str) -> dict[str, str]:
    """Return one configured figure record with its caption tokens resolved."""
    _require_variable("CONFIG_HASH")
    figures = _CONFIG.get("figures", {})
    if not isinstance(figures, dict):
        raise FigureConfigurationError("Manuscript figure metadata is not a mapping")
    for spec in figures.values():
        if not isinstance(spec, dict) or spec.get("filename") != filename:
            continue
        metadata = {str(key): str(value) for key, value in spec.items()}
        token_pattern = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
        metadata["caption"] = token_pattern.sub(
            lambda match: _require_variable(match.group(1)),
            metadata.get("caption", ""),
        )
        return metadata
    raise FigureConfigurationError(
        f"Figure {filename!r} is not present in manuscript config metadata"
    )


def _falsification_severity_map() -> dict[str, str]:
    """Return the generated live severity map without source-level fallback."""
    encoded = _var_str("CONFIG_FALSIFICATION_VECTOR_SEVERITIES")
    values = {
        name: severity
        for item in encoded.split(";")
        if "=" in item
        for name, severity in [item.split("=", 1)]
    }
    if not values:
        raise FigureConfigurationError(
            "Generated falsification severity map is empty or malformed"
        )
    return values


def _figure_provenance() -> str:
    version = _var_str("CONFIG_VERSION")
    config_hash = _var_str("CONFIG_HASH")
    generated = _var_str("GENERATION_TIMESTAMP")
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
