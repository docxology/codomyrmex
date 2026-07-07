#!/usr/bin/env python3
"""Generate publication-quality figures for the Codomyrmex manuscript.

Outputs to output/figures/:
  cover.png                  — dark bioluminescent colony network (cover art)
  colony_pressure_loop.png   — 8-step feedback cycle (circular flow)
  pheromone_decay.png        — FAST/NORMAL/SLOW decay curves
  gate_score_heatmap.png     — gate decision landscape (trust and risk pressure)
  trust_trajectory.png       — agent trust score across outcomes
  falsification_vectors.png  — 10 adversarial attack vectors (lollipop)
  subsystem_architecture.png — Colony Control Plane (hexagonal star topology)
"""

# SIZE_OK: Figure generation is centralized to keep manuscript visuals coherent.

from __future__ import annotations

import json
import math
import os
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
PROJECT_ROOT = Path(__file__).resolve().parent.parent
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


# ── Cover art ──────────────────────────────────────────────────────────────────


def fig_cover_art() -> None:
    BG = _COVER["bg"]
    W, H = 12.0, 6.5
    CX, CY = 0.0, 0.0

    fig = plt.figure(figsize=(W, H))
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_facecolor(BG)
    ax.set_xlim(-W / 2, W / 2)
    ax.set_ylim(-H / 2, H / 2)
    ax.set_aspect("equal")
    ax.axis("off")

    subsystems = [
        ("PheromoneStore", _COVER["phero"], "Pheromone\nStore"),
        ("ResourceLedger", _COVER["ledger"], "Resource\nLedger"),
        ("ActuationGate", _COVER["gate"], "Actuation\nGate"),
        ("ConsequenceMemory", _COVER["memory"], "Consequence\nMemory"),
        ("RoleAdapter", _COVER["role"], "Role\nAdapter"),
        ("PruningDaemon", _COVER["prune"], "Pruning\nDaemon"),
        ("FalsificationWorker", _COVER["falsif"], "Falsification\nWorker"),
    ]
    n_sub = len(subsystems)
    R_sub = 2.2
    R_label = 2.88
    R_outer = 3.45

    angles = [math.pi / 2 - 2 * math.pi * i / n_sub for i in range(n_sub)]
    sx = [R_sub * math.cos(a) for a in angles]
    sy = [R_sub * math.sin(a) for a in angles]

    # Hex grid background
    for row in range(-5, 6):
        for col in range(-10, 11):
            hx = col * 0.62 + (row % 2) * 0.31
            hy = row * 0.54
            if abs(hx) < W / 2 - 0.2 and abs(hy) < H / 2 - 0.1:
                ax.add_patch(
                    RegularPolygon(
                        (hx, hy),
                        numVertices=6,
                        radius=0.28,
                        orientation=0,
                        fill=False,
                        edgecolor=_COVER["grid"],
                        linewidth=0.30,
                        alpha=0.50,
                        zorder=0,
                    )
                )

    # Background radial glow
    for k in range(24, 0, -1):
        r = 0.12 + k * 0.19
        ax.add_patch(
            plt.Circle(
                (CX, CY),
                r,
                color=_COVER["kernel"],
                alpha=0.018 * (1 - k / 26),
                zorder=0,
            )
        )

    # Orbital ring
    theta = np.linspace(0, 2 * math.pi, 300)
    ax.plot(
        R_sub * np.cos(theta),
        R_sub * np.sin(theta),
        color="#1A2E42",
        lw=0.55,
        alpha=0.55,
        zorder=1,
    )

    # Ghostly spokes
    for i, (_, color, _) in enumerate(subsystems):
        ax.plot(
            [CX, sx[i]],
            [CY, sy[i]],
            color=color,
            alpha=0.09,
            lw=0.55,
            zorder=1,
            linestyle="--",
        )

    # Pheromone trails + particles
    n_particles = 11
    for i, (_, color, _) in enumerate(subsystems):
        bx, by = _bezier((sx[i], sy[i]), (CX, CY), curvature=0.38, n_pts=150)
        for seg in range(0, len(bx) - 4, 4):
            frac = seg / len(bx)
            ax.plot(
                bx[seg : seg + 5],
                by[seg : seg + 5],
                color=color,
                alpha=0.08 + frac * 0.28,
                lw=0.85,
                zorder=2,
            )
        bx2, by2 = _bezier((CX, CY), (sx[i], sy[i]), curvature=-0.20, n_pts=150)
        ax.plot(bx2, by2, color=color, alpha=0.09, lw=0.40, zorder=2, linestyle=":")
        for j in range(n_particles):
            frac = 0.05 + j * (0.90 / (n_particles - 1))
            idx = int(frac * (len(bx) - 1))
            ax.scatter(
                bx[idx],
                by[idx],
                color=color,
                s=5 + j * 9,
                alpha=0.65 + j * 0.03,
                zorder=4,
                linewidths=0,
            )

    # Outer agent ring (18 agents)
    n_agents = 18
    for k in range(n_agents):
        ag_a = 2 * math.pi * k / n_agents
        ax_pos = R_outer * math.cos(ag_a)
        ay_pos = R_outer * math.sin(ag_a)
        dists = [
            math.sqrt((ax_pos - sx[j]) ** 2 + (ay_pos - sy[j]) ** 2)
            for j in range(n_sub)
        ]
        nearest = int(np.argmin(dists))
        ag_color = subsystems[nearest][1]
        ax.plot(
            [ax_pos, sx[nearest]],
            [ay_pos, sy[nearest]],
            color=ag_color,
            alpha=0.07,
            lw=0.28,
            zorder=1,
        )
        _glow(
            ax,
            ax_pos,
            ay_pos,
            ag_color,
            r_core=0.038,
            r_max=0.13,
            n_rings=6,
            alpha_peak=0.22,
            zorder=3,
        )

    # Subsystem nodes
    for i, (_, color, short) in enumerate(subsystems):
        _glow(
            ax,
            sx[i],
            sy[i],
            color,
            r_core=0.23,
            r_max=0.68,
            n_rings=13,
            alpha_peak=0.17,
            zorder=5,
        )
        lx = R_label * math.cos(angles[i])
        ly = R_label * math.sin(angles[i])
        if i == 0:
            lx = sx[i]
            ly = sy[i] - 0.72
        ax.text(
            lx,
            ly,
            short,
            fontsize=6.5,
            color=color,
            ha="center",
            va="center",
            fontweight="bold",
            zorder=7,
            linespacing=1.4,
        )

    # ColonyKernel hub
    _glow(
        ax,
        CX,
        CY,
        _COVER["kernel"],
        r_core=0.34,
        r_max=0.98,
        n_rings=16,
        alpha_peak=0.21,
        zorder=6,
    )
    ax.text(
        CX,
        CY + 0.11,
        "Colony",
        fontsize=11,
        color="white",
        ha="center",
        va="center",
        fontweight="bold",
        zorder=9,
        fontfamily="monospace",
    )
    ax.text(
        CX,
        CY - 0.21,
        "Kernel",
        fontsize=11,
        color="white",
        ha="center",
        va="center",
        fontweight="bold",
        zorder=9,
        fontfamily="monospace",
    )

    # Title
    subtitle = _var_str(
        "CONFIG_SUBTITLE",
        "Colony Control Plane, Stigmergic Pressure, and Falsification-Gated Actuation",
    )
    ax.text(
        0,
        H / 2 - 0.24,
        "C O D O M Y R M E X",
        fontsize=22,
        color=_COVER["text"],
        ha="center",
        va="top",
        fontweight="bold",
        zorder=10,
        fontfamily="monospace",
    )
    ax.plot(
        [-2.6, 2.6],
        [H / 2 - 0.62, H / 2 - 0.62],
        color=_COVER["dim"],
        lw=0.75,
        alpha=0.50,
        zorder=10,
    )
    ax.text(
        0,
        H / 2 - 0.79,
        subtitle,
        fontsize=9,
        color=_COVER["dim"],
        ha="center",
        va="top",
        zorder=10,
        style="italic",
    )
    ax.text(
        -W / 2 + 0.14,
        -H / 2 + 0.14,
        "Colony Control Plane  ·  Stigmergic Pressure  ·  Falsification-Gated Actuation",
        fontsize=6,
        color=_COVER["dim"],
        ha="left",
        va="bottom",
        zorder=10,
    )
    ax.text(
        W / 2 - 0.14,
        -H / 2 + 0.14,
        _figure_provenance(),
        fontsize=5.8,
        color=_COVER["dim"],
        ha="right",
        va="bottom",
        zorder=10,
    )

    _save(fig, "cover.png")


# ── Figure 1 — Colony pressure loop ───────────────────────────────────────────


def fig_colony_pressure_loop() -> None:
    steps = [
        ("Environmental\nPressure", _OI["orange"], "1"),
        ("Proposal\nSubmission", _OI["sky"], "2"),
        ("Actuation\nGate", _OI["vermil"], "3"),
        ("Action\nExecution", _OI["blue"], "4"),
        ("Consequence\nRecord", _OI["green"], "5"),
        ("Trust &\nRole Update", _OI["pink"], "6"),
        ("Falsification\nReview", "#555555", "7"),
        ("Pheromone\nDeposit", _OI["orange"], "8"),
    ]
    n = len(steps)
    r = 2.9
    fig, ax = plt.subplots(figsize=(8.5, 8.5))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor("#F7F9FC")
    fig.patch.set_facecolor("#F7F9FC")
    ax.set_xlim(-r - 1.75, r + 1.75)
    ax.set_ylim(-r - 1.75, r + 1.75)

    angles = [math.pi / 2 - 2 * math.pi * i / n for i in range(n)]
    cx = [r * math.cos(a) for a in angles]
    cy = [r * math.sin(a) for a in angles]

    # Subtle concentric guide rings
    theta = np.linspace(0, 2 * math.pi, 300)
    for ring_r in [1.55, 2.90, 4.15]:
        ax.plot(
            ring_r * np.cos(theta),
            ring_r * np.sin(theta),
            color="#D0E4F0",
            lw=0.55,
            alpha=0.80,
            zorder=0,
        )

    # Curved arrows, color = source node
    for i in range(n):
        j = (i + 1) % n
        ax.annotate(
            "",
            xy=(cx[j], cy[j]),
            xytext=(cx[i], cy[i]),
            arrowprops={
                "arrowstyle": "-|>",
                "color": steps[i][1],
                "lw": 2.0,
                "mutation_scale": 17,
                "connectionstyle": "arc3,rad=0.18",
                "alpha": 0.65,
            },
            zorder=2,
        )

    # Node boxes
    box_w, box_h = 1.14, 0.66
    for i, (label, color, step_n) in enumerate(steps):
        # Shadow
        ax.add_patch(
            FancyBboxPatch(
                (cx[i] - box_w / 2 + 0.05, cy[i] - box_h / 2 - 0.05),
                box_w,
                box_h,
                boxstyle="round,pad=0.12",
                facecolor="#000000",
                alpha=0.10,
                linewidth=0,
                zorder=2,
            )
        )
        # Box
        ax.add_patch(
            FancyBboxPatch(
                (cx[i] - box_w / 2, cy[i] - box_h / 2),
                box_w,
                box_h,
                boxstyle="round,pad=0.12",
                facecolor=color,
                edgecolor="white",
                linewidth=2.5,
                zorder=3,
            )
        )
        text_color = (
            "white" if color not in (_OI["yellow"], _OI["orange"]) else "#1a1a1a"
        )
        ax.text(
            cx[i],
            cy[i] + 0.04,
            label,
            ha="center",
            va="center",
            fontsize=8.5,
            fontweight="bold",
            color=text_color,
            zorder=4,
            linespacing=1.25,
        )
        # Circular step badge
        badge_cx = cx[i] - box_w / 2 + 0.12
        badge_cy = cy[i] + box_h / 2 + 0.03
        ax.add_patch(
            plt.Circle((badge_cx, badge_cy), 0.11, color="white", alpha=0.88, zorder=5)
        )
        ax.text(
            badge_cx,
            badge_cy,
            step_n,
            ha="center",
            va="center",
            fontsize=7.5,
            fontweight="bold",
            color=color,
            zorder=6,
        )

    # Hub with glow rings
    for ring_r, alpha in [(0.98, 0.07), (0.78, 0.13), (0.56, 0.20)]:
        ax.add_patch(
            plt.Circle(
                (0, 0),
                ring_r,
                facecolor=_OI["sky"],
                edgecolor="none",
                alpha=alpha,
                zorder=3,
            )
        )
    ax.add_patch(
        plt.Circle(
            (0, 0),
            0.70,
            facecolor=_OI["sky"],
            edgecolor="white",
            linewidth=2.5,
            alpha=0.97,
            zorder=4,
        )
    )
    ax.text(
        0,
        0.14,
        "Colony",
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold",
        color="white",
        zorder=6,
    )
    ax.text(
        0,
        -0.12,
        "Control",
        ha="center",
        va="center",
        fontsize=8.5,
        color="white",
        alpha=0.90,
        zorder=6,
    )
    ax.text(
        0,
        -0.34,
        "Plane",
        ha="center",
        va="center",
        fontsize=8.5,
        color="white",
        alpha=0.90,
        zorder=6,
    )

    ax.set_title(
        "Colony feedback loop — 8-step circular actuation cycle\n"
        "Each proposal traverses the full ring before state is committed",
        fontsize=11,
        pad=16,
        color="#1a1a1a",
    )
    _add_provenance_note(fig)
    fig.tight_layout(pad=0.4, rect=(0, 0.035, 1, 1))
    _save(fig, "colony_pressure_loop.png")


# ── Figure 2 — Pheromone decay curves ─────────────────────────────────────────


def fig_pheromone_decay() -> None:
    t = np.linspace(0, 10, 600)
    base_rate = _experiment_float(
        "base_evaporation_rate", "CONFIG_BASE_EVAPORATION_RATE", 0.10
    )
    fast_mult = _var_float("CONFIG_DECAY_RATE_FAST", 3.0)
    normal_mult = _var_float("CONFIG_DECAY_RATE_NORMAL", 1.0)
    slow_mult = _var_float("CONFIG_DECAY_RATE_SLOW", 0.2)
    configs = [
        (
            f"FAST  (λ={base_rate * fast_mult:.2f}) — FAILURE, RISK",
            base_rate * fast_mult,
            _OI["vermil"],
            "solid",
            "FAST",
        ),
        (
            f"NORMAL (λ={base_rate * normal_mult:.2f}) — NEED, DEPENDENCY",
            base_rate * normal_mult,
            _OI["blue"],
            "dashed",
            "NORMAL",
        ),
        (
            f"SLOW  (λ={base_rate * slow_mult:.2f}) — SUCCESS, PRIORITY",
            base_rate * slow_mult,
            _OI["green"],
            "dotted",
            "SLOW",
        ),
    ]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.set_facecolor("#F7F9FC")
    fig.patch.set_facecolor("#F7F9FC")
    _pub_style(ax)

    for label, rate, color, ls, cls_name in configs:
        strength = np.exp(-rate * t)
        ax.plot(t, strength, label=label, color=color, linestyle=ls, lw=2.8, zorder=4)
        ax.fill_between(t, 0, strength, color=color, alpha=0.07, zorder=2)
        ax.fill_between(
            t, 0, np.minimum(strength, 0.50), color=color, alpha=0.05, zorder=2
        )

        # Time-constant marker (τ = 1/λ), value = 1/e ≈ 0.368
        tau = 1.0 / rate
        if tau <= 10.0:
            s_tau = math.exp(-1.0)  # always 1/e
            ax.vlines(
                tau,
                0,
                s_tau,
                colors=color,
                linestyles=":",
                lw=1.0,
                alpha=0.50,
                zorder=3,
            )
            ax.hlines(
                s_tau,
                0,
                tau,
                colors=color,
                linestyles=":",
                lw=1.0,
                alpha=0.50,
                zorder=3,
            )
            ax.scatter(
                [tau],
                [s_tau],
                color=color,
                s=60,
                zorder=5,
                edgecolors="white",
                linewidths=1.2,
            )

        # Curve label (direct)
        idx = int(3.6 / 10.0 * len(t))
        y_lbl = strength[idx]
        if y_lbl > 0.02:
            offsets = {"FAST": -0.07, "NORMAL": 0.04, "SLOW": 0.025}
            ax.text(
                3.7,
                y_lbl + offsets[cls_name],
                cls_name,
                fontsize=9,
                color=color,
                fontweight="bold",
                va="center",
                bbox={
                    "boxstyle": "round,pad=0.20",
                    "facecolor": "white",
                    "edgecolor": color,
                    "alpha": 0.88,
                    "linewidth": 1.0,
                },
            )

    # 50% line
    ax.axhline(
        y=0.5,
        color=_OI["grey"],
        linestyle="--",
        lw=1.2,
        alpha=0.55,
        label="50% threshold",
    )
    ax.text(0.12, 0.515, "50%", fontsize=8, color=_OI["grey"], va="bottom")

    # FAST half-life annotation
    fast_rate = base_rate * fast_mult
    t_half = math.log(2) / fast_rate
    ax.annotate(
        f"FAST t½ = {t_half:.2f} ticks",
        xy=(t_half, 0.5),
        xytext=(t_half + 0.65, 0.63),
        arrowprops={"arrowstyle": "->", "color": _OI["vermil"], "lw": 1.1},
        fontsize=8.5,
        color=_OI["vermil"],
        bbox={
            "boxstyle": "round,pad=0.25",
            "facecolor": "white",
            "edgecolor": _OI["vermil"],
            "alpha": 0.90,
        },
    )

    slow_rate = base_rate * slow_mult
    slow_per_tick = math.exp(-slow_rate)
    slow_example_tick = 8.0
    slow_example_strength = math.exp(-slow_rate * slow_example_tick)
    slow_half_life = math.log(2) / slow_rate
    ax.annotate(
        f"SLOW: {slow_per_tick:.0%} retained per tick\n"
        f"(e^(-{slow_rate:.2f}) ≈ {slow_per_tick:.3f}; t½ ≈ {slow_half_life:.2f} ticks)",
        xy=(slow_example_tick, slow_example_strength),
        xytext=(6.1, 0.68),
        arrowprops={"arrowstyle": "->", "color": _OI["green"], "lw": 1.1},
        fontsize=8.0,
        color=_OI["green"],
        ha="center",
        bbox={
            "boxstyle": "round,pad=0.28",
            "facecolor": "white",
            "edgecolor": _OI["green"],
            "alpha": 0.90,
        },
    )

    ax.set_xlabel("Ticks since deposit", fontsize=11.5, color="#333333")
    ax.set_ylabel(
        "Pheromone signal strength (normalised)", fontsize=11.5, color="#333333"
    )
    ax.set_title(
        "Pheromone signal decay by rate class\n"
        "s(t) = s0 exp(-lambda t) — three config-backed rate classes map to signal volatility",
        fontsize=11,
        pad=12,
    )
    ax.legend(fontsize=9, loc="upper right", framealpha=0.92, edgecolor="#CCCCCC")
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.02, 1.10)
    _add_provenance_note(fig)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    _save(fig, "pheromone_decay.png")


# ── Figure 3 — Gate score heatmap ─────────────────────────────────────────────


def fig_gate_score_heatmap() -> None:
    N = 160
    trust_vals = np.linspace(0.0, 1.0, N)
    pressure_vals = np.linspace(0.0, 10.0, N)
    T, P = np.meshgrid(trust_vals, pressure_vals)

    w_budget = _gate_weight("budget", 0.30)
    w_risk = _gate_weight("risk", 0.30)
    w_trust = _gate_weight("trust", 0.25)
    w_completeness = _gate_weight("completeness", 0.15)
    hold_threshold = _experiment_float(
        "gate_hold_threshold", "CONFIG_GATE_HOLD_THRESHOLD", 0.50
    )
    execute_threshold = _experiment_float(
        "gate_execute_threshold",
        "CONFIG_GATE_EXECUTE_THRESHOLD",
        0.75,
    )
    trust_hard_floor = _experiment_float(
        "trust_hard_floor", "CONFIG_TRUST_HARD_FLOOR", 0.30
    )
    trust_full_credit = 0.60

    risk_ok = np.where(P < 3.0, 1.0, np.where(P < 6.0, 0.5, 0.0))
    trust_ok = np.where(trust_full_credit <= T, 1.0, 0.5)
    score = (
        w_budget * np.ones_like(T)
        + w_risk * risk_ok
        + w_trust * trust_ok
        + w_completeness
    )
    score = np.where(trust_hard_floor > T, 0.0, score)

    cmap = ListedColormap(["#7F1D1D", "#F4B44A", "#0A7A43"], name="gate_decision")
    norm = BoundaryNorm([0.0, hold_threshold, execute_threshold, 1.001], cmap.N)

    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    ax.set_facecolor("#080808")
    fig.patch.set_facecolor("#F7F9FC")

    im = ax.pcolormesh(
        trust_vals, pressure_vals, score, cmap=cmap, norm=norm, shading="auto"
    )

    cbar_ticks = [
        hold_threshold / 2,
        (hold_threshold + execute_threshold) / 2,
        (execute_threshold + 1.0) / 2,
    ]
    cbar = fig.colorbar(im, ax=ax, pad=0.02, shrink=0.96, ticks=cbar_ticks)
    cbar.ax.tick_params(labelsize=9)
    cbar.ax.set_yticklabels(
        [
            f"REFUSE\n<{hold_threshold:.2f}",
            f"HOLD\n{hold_threshold:.2f}-{execute_threshold:.2f}",
            f"EXECUTE\n>={execute_threshold:.2f}",
        ]
    )
    cbar.set_label("Decision band", fontsize=10)

    # Boundary contours
    ax.contour(
        trust_vals,
        pressure_vals,
        score,
        levels=[hold_threshold, execute_threshold],
        colors=["#FFE066", "white"],
        linestyles=["--", "-"],
        linewidths=[2.0, 2.5],
    )

    ax.axvspan(0.0, trust_hard_floor, alpha=0.62, color="#000000", zorder=2)
    ax.text(
        trust_hard_floor / 2,
        9.2,
        "TRUST\nHARD FLOOR",
        fontsize=7.5,
        color="white",
        ha="center",
        va="top",
        fontweight="bold",
        zorder=3,
    )

    # Decision region labels
    ax.text(
        0.88,
        1.2,
        "EXECUTE",
        fontsize=12,
        color="white",
        fontweight="bold",
        ha="center",
        va="center",
        zorder=3,
        alpha=0.90,
    )
    ax.text(
        0.48,
        5.8,
        "HOLD",
        fontsize=12,
        color="white",
        fontweight="bold",
        ha="center",
        va="center",
        zorder=3,
        alpha=0.90,
    )
    ax.text(
        0.18,
        8.3,
        "REFUSE",
        fontsize=12,
        color="white",
        fontweight="bold",
        ha="center",
        va="center",
        zorder=3,
        alpha=0.90,
    )

    # Trust threshold verticals
    for x_val, label_txt in [
        (trust_hard_floor, "hard\nfloor"),
        (trust_full_credit, "full\ntrust"),
    ]:
        ax.axvline(x=x_val, color="white", lw=0.8, alpha=0.35, linestyle=":")
        ax.text(
            x_val + 0.006,
            9.72,
            f"{x_val} {label_txt.replace(chr(10), ' ')}",
            fontsize=7.2,
            color="white",
            ha="left",
            alpha=0.82,
            zorder=3,
            va="top",
        )

    for y_val, label_txt in [(3.0, "medium risk"), (6.0, "high risk")]:
        ax.axhline(y=y_val, color="white", lw=0.8, alpha=0.32, linestyle=":")
        ax.text(
            0.985,
            y_val + 0.08,
            label_txt,
            fontsize=7.2,
            color="white",
            ha="right",
            va="bottom",
            alpha=0.82,
            zorder=3,
        )

    def _score_at(trust_score: float, risk_pressure: float) -> float:
        if trust_score < trust_hard_floor:
            return 0.0
        risk_component = (
            1.0 if risk_pressure < 3.0 else 0.5 if risk_pressure < 6.0 else 0.0
        )
        trust_component = 1.0 if trust_score >= trust_full_credit else 0.5
        return (
            w_budget
            + w_risk * risk_component
            + w_trust * trust_component
            + w_completeness
        )

    def _decision(score_value: float) -> str:
        if score_value >= execute_threshold:
            return "EXECUTE"
        if score_value >= hold_threshold:
            return "HOLD"
        return "REFUSE"

    examples = [
        (0.90, 1.0, 0.73, 1.70, "GUARD_ANT\nfull spec", "white"),
        (0.70, 6.5, 0.78, 7.30, "elevated\nrisk", "#FFE066"),
        (0.20, 1.0, 0.33, 1.90, "low trust\nclear field", "#FF9999"),
    ]
    for tx, tp, label_x, label_y, desc, ecolor in examples:
        sc = _score_at(tx, tp)
        decision = _decision(sc)
        ax.scatter(
            [tx],
            [tp],
            color=ecolor,
            s=115,
            zorder=6,
            edgecolors="white",
            linewidths=1.8,
        )
        ax.annotate(
            f"{desc}\nscore={sc:.2f} → {decision}",
            xy=(tx, tp),
            xytext=(label_x, label_y),
            fontsize=7,
            color=ecolor,
            arrowprops={"arrowstyle": "-", "color": ecolor, "lw": 0.8, "alpha": 0.75},
            bbox={
                "boxstyle": "round,pad=0.22",
                "facecolor": "#00000099",
                "edgecolor": ecolor,
                "alpha": 0.92,
            },
        )

    ax.set_xlabel("Agent trust score", fontsize=11.5)
    ax.set_ylabel("Risk pheromone pressure", fontsize=11.5)
    gate_title = (
        "Gate decision landscape — piecewise score bands and hard trust floor\n"
        f"score = {w_budget:.2f}*budget + {w_risk:.2f}*risk_ok + "
        f"{w_trust:.2f}*trust_ok + {w_completeness:.2f}*completeness\n"
        f"(budget=1.0, completeness=1.0; trust_ok tiers at {trust_full_credit:.2f}; "
        f"trust < {trust_hard_floor:.2f} forces score=0)"
    )
    ax.set_title(gate_title, fontsize=9.5, pad=10)
    ax.tick_params(labelsize=9.5)
    _add_provenance_note(fig, color="#6B7280")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    _save(fig, "gate_score_heatmap.png")


# ── Figure 4 — Trust trajectory ───────────────────────────────────────────────


def fig_trust_trajectory() -> None:
    trust_init = _var_float(
        "RESULT_TRUST_INITIAL",
        _experiment_float("trust_sandbox_score", "CONFIG_TRUST_SANDBOX_SCORE", 0.10),
    )
    delta = _experiment_float("trust_delta_pass", "CONFIG_TRUST_DELTA_PASS", 0.04)
    repair_threshold = _role_threshold("repair_ant", "min_trust", 0.20)
    memory_threshold = _role_threshold("memory_ant", "min_trust", 0.35)
    dispatcher_threshold = _role_threshold("dispatcher", "min_trust", 0.50)
    guard_threshold = _role_threshold("guard_ant", "min_trust", 0.70)
    proposal_min = _role_min_proposals("repair_ant", 3)
    trust_hard_floor = _experiment_float(
        "trust_hard_floor", "CONFIG_TRUST_HARD_FLOOR", 0.30
    )
    # Outcomes 0–12 (the manuscript window)
    outcomes = list(range(13))
    trust = [min(trust_init + i * delta, 1.0) for i in outcomes]

    def _role(outcome: int, tv: float) -> str:
        if outcome < proposal_min or tv < repair_threshold:
            return "SANDBOX"
        if tv >= guard_threshold:
            return "GUARD_ANT"
        if tv >= dispatcher_threshold:
            return "DISPATCHER"
        if tv >= memory_threshold:
            return "MEMORY_ANT"
        if tv >= repair_threshold:
            return "REPAIR_ANT"
        return "SANDBOX"

    def _first_outcome_for(threshold: float) -> int:
        if delta <= 0:
            return proposal_min
        return max(proposal_min, math.ceil((threshold - trust_init) / delta))

    roles = [_role(i, tv) for i, tv in enumerate(trust)]
    sandbox_c = _OI["orange"]
    repair_c = _OI["green"]
    disp_c = _OI["blue"]
    memory_c = _OI["sky"]
    guard_c = _OI["vermil"]
    role_col = {
        "SANDBOX": sandbox_c,
        "REPAIR_ANT": repair_c,
        "MEMORY_ANT": memory_c,
        "DISPATCHER": disp_c,
        "GUARD_ANT": guard_c,
    }
    col_pts = [role_col[r] for r in roles]

    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    ax.set_facecolor("#F7F9FC")
    fig.patch.set_facecolor("#F7F9FC")
    _pub_style(ax)

    repair_idx = next((i for i, r in enumerate(roles) if r == "REPAIR_ANT"), None)

    repair_start = _first_outcome_for(repair_threshold)
    memory_start = _first_outcome_for(memory_threshold)
    dispatcher_start = _first_outcome_for(dispatcher_threshold)
    guard_start = _first_outcome_for(guard_threshold)
    horizon_end = max(18, guard_start + 2)

    # Zone shading
    zone_spans = [
        (-0.5, repair_start - 0.5, sandbox_c, "SANDBOX"),
        (repair_start - 0.5, memory_start - 0.5, repair_c, "REPAIR_ANT"),
        (memory_start - 0.5, dispatcher_start - 0.5, memory_c, "MEMORY_ANT"),
        (dispatcher_start - 0.5, guard_start - 0.5, disp_c, "DISPATCHER"),
        (guard_start - 0.5, horizon_end + 0.5, guard_c, "GUARD_ANT"),
    ]
    for start, end, color, _label in zone_spans:
        ax.axvspan(start, end, alpha=0.07, color=color)

    # Zone labels
    for start, end, color, label in zone_spans[:4]:
        ax.text(
            (start + end) / 2,
            0.045,
            label,
            ha="center",
            va="bottom",
            fontsize=7.8,
            color=color,
            alpha=0.85,
            fontweight="bold",
        )

    # Thresholds
    ax.axhline(
        y=trust_init,
        color=_OI["grey"],
        linestyle=":",
        lw=1.2,
        alpha=0.55,
        label=f"Entry floor ({trust_init:.2f})",
    )
    threshold_lines = [
        (repair_threshold, repair_c, f"First promotion floor ({repair_threshold:.2f})"),
        (trust_hard_floor, sandbox_c, f"Gate hard floor ({trust_hard_floor:.2f})"),
        (memory_threshold, memory_c, f"MEMORY_ANT threshold ({memory_threshold:.2f})"),
        (
            dispatcher_threshold,
            disp_c,
            f"DISPATCHER threshold ({dispatcher_threshold:.2f})",
        ),
        (guard_threshold, guard_c, f"GUARD_ANT threshold ({guard_threshold:.2f})"),
    ]
    for yval, color, label in threshold_lines:
        ax.axhline(
            y=yval,
            color=color,
            linestyle="--" if yval >= 0.50 else ":",
            lw=1.4,
            alpha=0.72,
            label=label,
        )
    for yval, color in [
        (repair_threshold, repair_c),
        (trust_hard_floor, sandbox_c),
        (memory_threshold, memory_c),
        (dispatcher_threshold, disp_c),
        (guard_threshold, guard_c),
    ]:
        ax.text(
            -0.48,
            yval + 0.008,
            f"{yval:.2f}",
            fontsize=7.5,
            color=color,
            va="bottom",
            alpha=0.88,
        )

    # Gradient line (segment per role)
    for i in range(len(outcomes) - 1):
        seg_color = col_pts[i]
        ax.plot(
            outcomes[i : i + 2],
            trust[i : i + 2],
            color=seg_color,
            lw=2.9,
            zorder=3,
            solid_capstyle="round",
        )
        ax.fill_between(
            outcomes[i : i + 2],
            trust_init - 0.01,
            trust[i : i + 2],
            color=seg_color,
            alpha=0.08,
            zorder=2,
        )

    future_outcomes = list(range(12, horizon_end + 1))
    future_trust = [min(trust_init + i * delta, 1.0) for i in future_outcomes]
    ax.plot(
        future_outcomes,
        future_trust,
        color=guard_c,
        lw=1.8,
        linestyle="--",
        alpha=0.40,
        zorder=2,
    )
    guard_outcome = next(
        (
            i
            for i in future_outcomes
            if min(trust_init + i * delta, 1.0) >= guard_threshold
        ),
        None,
    )
    if guard_outcome is not None:
        ax.scatter(
            [guard_outcome],
            [guard_threshold],
            color=guard_c,
            s=90,
            alpha=0.45,
            zorder=3,
            edgecolors="white",
            linewidths=1.2,
        )
        ax.text(
            guard_outcome + 0.2,
            guard_threshold + 0.02,
            f"~outcome {guard_outcome}\nGUARD_ANT",
            fontsize=7,
            color=guard_c,
            alpha=0.60,
            va="bottom",
        )

    # Scatter
    ax.scatter(
        outcomes, trust, c=col_pts, s=150, zorder=6, edgecolors="white", linewidths=1.5
    )

    # Checkpoint labels
    for idx in [0, 3, 6, 9, 12]:
        if idx < len(trust):
            ax.text(
                idx,
                trust[idx] + 0.025,
                f"{trust[idx]:.2f}",
                ha="center",
                va="bottom",
                fontsize=8.5,
                color="#222222",
                fontweight="bold",
            )

    # Graduation annotation
    if repair_idx is not None:
        ax.annotate(
            f"Outcome {repair_idx}: SANDBOX → REPAIR_ANT\n"
            f"(trust = {trust[repair_idx]:.2f} ≥ {repair_threshold:.2f} "
            f"and proposals ≥ {proposal_min})",
            xy=(repair_idx, trust[repair_idx]),
            xytext=(repair_idx + 2.2, trust[repair_idx] - 0.075),
            arrowprops={"arrowstyle": "-|>", "color": repair_c, "lw": 1.5},
            fontsize=8.5,
            color=repair_c,
            fontweight="bold",
            bbox={
                "boxstyle": "round,pad=0.35",
                "facecolor": "white",
                "edgecolor": repair_c,
                "alpha": 0.92,
                "linewidth": 1.5,
            },
        )

    # Legend
    legend_items = [
        mpatches.Patch(color=sandbox_c, label=f"SANDBOX (<{proposal_min} proposals)"),
        mpatches.Patch(
            color=repair_c,
            label=f"REPAIR_ANT (≥{repair_threshold:.2f} + {proposal_min} proposals)",
        ),
        mpatches.Patch(color=memory_c, label=f"MEMORY_ANT (≥{memory_threshold:.2f})"),
        mpatches.Patch(color=disp_c, label=f"DISPATCHER (≥{dispatcher_threshold:.2f})"),
        mpatches.Patch(
            color=guard_c, label=f"GUARD_ANT (≥{guard_threshold:.2f}, projected)"
        ),
        plt.Line2D(
            [],
            [],
            color=_OI["grey"],
            linestyle=":",
            lw=1.5,
            label=f"Entry floor ({trust_init:.2f})",
        ),
        plt.Line2D(
            [],
            [],
            color=sandbox_c,
            linestyle=":",
            lw=1.5,
            label=f"Gate hard floor ({trust_hard_floor:.2f})",
        ),
    ]
    ax.legend(
        handles=legend_items,
        fontsize=8,
        loc="upper left",
        ncol=2,
        framealpha=0.92,
        edgecolor="#CCCCCC",
    )

    ax.set_xlabel("Outcome number (consecutive successful passes)", fontsize=11.5)
    ax.set_ylabel("Agent trust score", fontsize=11.5)
    trust_at_12 = min(trust_init + 12 * delta, 1.0)
    ax.set_title(
        f"Trust trajectory — conservative model (Δ = {delta:.2f} per pass)\n"
        f"trust {trust_init:.2f} → {trust_at_12:.2f} after 12 outcomes; "
        "dashed projection shows GUARD_ANT crossing",
        fontsize=10.5,
        pad=12,
    )
    ax.set_xlim(-0.5, horizon_end)
    ax.set_ylim(0.0, 0.84)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.tick_params(labelsize=9.5)
    _add_provenance_note(fig)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    _save(fig, "trust_trajectory.png")


# ── Figure 5 — Falsification vectors (lollipop) ───────────────────────────────


def fig_falsification_vectors() -> None:
    vectors = [
        ("SECURITY_RISK", "HIGH", _OI["vermil"]),
        ("NO_ROLLBACK", "HIGH", _OI["vermil"]),
        ("NO_TEST_VALUE", "HIGH", _OI["vermil"]),
        ("SCOPE_CREEP", "HIGH", _OI["vermil"]),
        ("CIRCULAR_ARCHITECTURE", "HIGH", _OI["vermil"]),
        ("FALSE_METRIC", "MEDIUM", _OI["orange"]),
        ("HIDDEN_MAINTENANCE_COST", "MEDIUM", _OI["orange"]),
        ("DEPENDENCY_RISK", "MEDIUM", _OI["orange"]),
        ("OVER_BROAD_MODULE", "MEDIUM", _OI["orange"]),
        ("PREMATURE_ABSTRACTION", "LOW", _OI["sky"]),
    ]
    sev_weight = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    names = [v[0] for v in vectors]
    weights = [sev_weight[v[1]] for v in vectors]
    colors = [v[2] for v in vectors]
    labels = [v[1] for v in vectors]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.set_facecolor("#F7F9FC")
    fig.patch.set_facecolor("#F7F9FC")
    _pub_style(ax)

    y_pos = list(range(len(names)))

    # Severity band backgrounds
    for x0, x1, bcolor, balpha in [
        (3.5, 4.55, _OI["black"], 0.06),
        (2.5, 3.5, _OI["vermil"], 0.05),
        (1.5, 2.5, _OI["orange"], 0.04),
        (0.5, 1.5, _OI["sky"], 0.04),
    ]:
        ax.axvspan(x0, x1, alpha=balpha, color=bcolor, zorder=0)

    # Lollipop stems
    for i, (w, color) in enumerate(zip(weights, colors, strict=False)):
        ax.plot(
            [0, w],
            [y_pos[i], y_pos[i]],
            color=color,
            lw=2.0,
            alpha=0.55,
            zorder=2,
            solid_capstyle="round",
        )

    # Lollipop heads
    ax.scatter(
        weights, y_pos, c=colors, s=220, zorder=4, edgecolors="white", linewidths=2.0
    )

    # Severity letter inside head
    for i, (w, sev, color) in enumerate(zip(weights, labels, colors, strict=False)):
        txt_color = "white" if color not in (_OI["sky"], _OI["yellow"]) else "#1a1a1a"
        ax.text(
            w,
            y_pos[i],
            sev[0],  # C / H / M / L
            va="center",
            ha="center",
            fontsize=7.5,
            color=txt_color,
            fontweight="bold",
            zorder=5,
        )

    ax.text(
        3.76,
        5.45,
        "CRITICAL override class\n(no canonical vector currently\nlands here)",
        fontsize=8.2,
        color="#333333",
        ha="center",
        va="center",
        bbox={
            "boxstyle": "round,pad=0.35",
            "facecolor": "#FFF0EE",
            "edgecolor": _OI["vermil"],
            "alpha": 0.95,
            "linewidth": 1.5,
        },
    )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=9, fontfamily="monospace")
    ax.set_xlabel("Severity weight", fontsize=11.5, color="#333333")
    ax.set_xticks([1, 2, 3, 4])
    ax.set_xticklabels(
        ["LOW (1)", "MEDIUM (2)", "HIGH (3)", "CRITICAL (4)"], fontsize=9.5
    )
    ax.set_title(
        f"FalsificationWorker — {len(vectors)} canonical adversarial vectors\n"
        "Current checks top out at HIGH; CRITICAL remains the unconditional gate override class",
        fontsize=11,
        pad=12,
    )

    legend_items = [
        mpatches.Patch(color=_OI["black"], label="CRITICAL override class"),
        mpatches.Patch(color=_OI["vermil"], label="HIGH — strong REFUSE signal"),
        mpatches.Patch(color=_OI["orange"], label="MEDIUM — HOLD candidate"),
        mpatches.Patch(color=_OI["sky"], label="LOW — advisory"),
    ]
    ax.legend(
        handles=legend_items,
        fontsize=8.2,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.11),
        framealpha=0.92,
        ncol=4,
        edgecolor="#CCCCCC",
    )

    ax.invert_yaxis()
    ax.set_xlim(0, 4.7)
    _add_provenance_note(fig)
    fig.tight_layout(rect=(0, 0.095, 1, 1))
    _save(fig, "falsification_vectors.png")


# ── Figure 6 — Subsystem architecture (hexagonal star) ────────────────────────


def fig_subsystem_architecture() -> None:
    subsystem_total = _var_str("CONFIG_COLONY_KERNEL_SUBSYSTEMS", "8")
    subsystems = [
        ("Pheromone\nStore", _OI["orange"], "Stigmergic\ntraces & decay"),
        ("Resource\nLedger", _OI["blue"], "Budget\nenforcement"),
        ("Actuation\nGate", _OI["vermil"], "Permission\nscoring gate"),
        ("Consequence\nMemory", _OI["green"], "SQLite\noutcome log"),
        ("Role\nAdapter", _OI["pink"], "Trust → role\ninference"),
        ("Pruning\nDaemon", _OI["grey"], "Stale module\neviction"),
        ("Falsification\nWorker", "#444444", "Adversarial\npre-check"),
    ]
    n = len(subsystems)
    r = 3.0
    fig, ax = plt.subplots(figsize=(9.5, 9.5))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor("#F4F7FC")
    fig.patch.set_facecolor("#F4F7FC")
    ax.set_xlim(-r - 1.85, r + 1.85)
    ax.set_ylim(-r - 1.85, r + 1.85)

    angles = [math.pi / 2 - 2 * math.pi * i / n for i in range(n)]
    cx = [r * math.cos(a) for a in angles]
    cy = [r * math.sin(a) for a in angles]

    # Concentric guide rings
    theta = np.linspace(0, 2 * math.pi, 300)
    for ring_r in [1.2, 2.2, 3.0, 4.25]:
        ax.plot(
            ring_r * np.cos(theta),
            ring_r * np.sin(theta),
            color="#CCD8E8",
            lw=0.55,
            alpha=0.60,
            zorder=0,
        )

    # Spokes: outbound arrow only, plus thin return line
    for i, (name, color, subtitle) in enumerate(subsystems):
        ax.plot(
            [cx[i] * 0.32, cx[i] * 0.84],
            [cy[i] * 0.32, cy[i] * 0.84],
            color=color,
            alpha=0.20,
            lw=1.8,
            zorder=1,
        )
        ax.annotate(
            "",
            xy=(cx[i] * 0.86, cy[i] * 0.86),
            xytext=(cx[i] * 0.32, cy[i] * 0.32),
            arrowprops={
                "arrowstyle": "-|>",
                "color": color,
                "alpha": 0.55,
                "lw": 1.5,
                "mutation_scale": 12,
            },
            zorder=2,
        )
        # Thin return (kernel ← subsystem)
        ax.annotate(
            "",
            xy=(cx[i] * 0.35, cy[i] * 0.35),
            xytext=(cx[i] * 0.74, cy[i] * 0.74),
            arrowprops={
                "arrowstyle": "-|>",
                "color": _OI["sky"],
                "alpha": 0.28,
                "lw": 0.85,
                "mutation_scale": 9,
            },
            zorder=1,
        )

    # Hexagonal subsystem nodes
    hex_r = 0.60
    for i, (name, color, subtitle) in enumerate(subsystems):
        # Shadow
        ax.add_patch(
            RegularPolygon(
                (cx[i] + 0.06, cy[i] - 0.06),
                numVertices=6,
                radius=hex_r,
                orientation=0,
                facecolor="#000000",
                alpha=0.09,
                edgecolor="none",
                zorder=2,
            )
        )
        # Main hex
        ax.add_patch(
            RegularPolygon(
                (cx[i], cy[i]),
                numVertices=6,
                radius=hex_r,
                orientation=0,
                facecolor=color,
                edgecolor="white",
                linewidth=2.2,
                zorder=3,
            )
        )
        text_color = "white" if color != _OI["yellow"] else "#1a1a1a"
        ax.text(
            cx[i],
            cy[i] + 0.17,
            name,
            ha="center",
            va="center",
            fontsize=7.1,
            fontweight="bold",
            color=text_color,
            zorder=5,
            linespacing=1.0,
        )
        ax.text(
            cx[i],
            cy[i] - 0.24,
            subtitle,
            ha="center",
            va="center",
            fontsize=6.5,
            color=text_color,
            alpha=0.88,
            zorder=5,
            linespacing=1.3,
        )

    # Centre hexagonal hub (ColonyKernel) with glow rings
    for glow_r, galpha in [(1.22, 0.06), (0.98, 0.10), (0.80, 0.17)]:
        ax.add_patch(
            RegularPolygon(
                (0, 0),
                numVertices=6,
                radius=glow_r,
                orientation=0,
                facecolor=_OI["sky"],
                edgecolor="none",
                alpha=galpha,
                zorder=2,
            )
        )
    ax.add_patch(
        RegularPolygon(
            (0, 0),
            numVertices=6,
            radius=0.76,
            orientation=0,
            facecolor=_OI["sky"],
            edgecolor="white",
            linewidth=2.8,
            alpha=0.97,
            zorder=4,
        )
    )
    ax.text(
        0,
        0.14,
        "Colony",
        ha="center",
        va="center",
        fontsize=12.5,
        fontweight="bold",
        color="white",
        zorder=6,
    )
    ax.text(
        0,
        -0.16,
        "Kernel",
        ha="center",
        va="center",
        fontsize=12.5,
        fontweight="bold",
        color="white",
        zorder=6,
    )
    ax.text(
        0,
        -0.52,
        f"{subsystem_total} subsystems",
        ha="center",
        va="center",
        fontsize=6.8,
        color="white",
        alpha=0.88,
        zorder=6,
    )

    ax.set_title(
        f"Colony Control Plane — {subsystem_total}-subsystem star topology\n"
        "ColonyKernel sequences state; leaves exchange typed value objects from models.py",
        fontsize=11,
        pad=14,
        color="#1a1a1a",
    )
    _add_provenance_note(fig)
    fig.tight_layout(pad=0.4, rect=(0, 0.035, 1, 1))
    _save(fig, "subsystem_architecture.png")


# ── NEW: Figure — 3D gate score landscape ─────────────────────────────────────


def fig_gate_score_3d() -> None:
    """3D surface: gate score g(trust, risk, completeness) with budget=1.0.

    Used by 02_theory.md to illustrate the score as a bounded risk-monotone
    function and the EXECUTE/HOLD/REFUSE decision boundaries.
    """
    from mpl_toolkits.mplot3d import Axes3D

    w_trust = _var_float("CONFIG_GATE_WEIGHT_TRUST", 0.25)
    w_complete = _var_float("CONFIG_GATE_WEIGHT_COMPLETENESS", 0.15)
    gate_exec = _var_float("CONFIG_GATE_EXECUTE_THRESHOLD", 0.75)
    gate_hold = _var_float("CONFIG_GATE_HOLD_THRESHOLD", 0.50)

    trust = np.linspace(0, 1, 60)
    completeness = np.linspace(0, 1, 60)
    T, C = np.meshgrid(trust, completeness)

    # Gate score with budget_ok=1 and risk_ok=1 (best case for trust × completeness)
    score_best = 0.30 + 0.30 + w_trust * T + w_complete * C

    fig = plt.figure(figsize=(11, 5.5))
    fig.patch.set_facecolor("#F7F9FC")

    # ── Left panel: full 3D surface ──
    ax1 = fig.add_subplot(1, 2, 1, projection="3d")
    ax1.view_init(elev=28, azim=-55)
    ax1.xaxis.pane.fill = False
    ax1.yaxis.pane.fill = False
    ax1.zaxis.pane.fill = False
    ax1.xaxis.pane.set_edgecolor("#CCCCCC")
    ax1.yaxis.pane.set_edgecolor("#CCCCCC")
    ax1.zaxis.pane.set_edgecolor("#CCCCCC")

    norm = plt.Normalize(0, 1)
    surf = ax1.plot_surface(
        T,
        C,
        score_best,
        facecolors=plt.cm.YlOrRd(norm(score_best)),
        alpha=0.92,
        linewidth=0,
        antialiased=True,
    )

    ax1.set_xlabel("Trust score", fontsize=9, labelpad=8)
    ax1.set_ylabel("Completeness", fontsize=9, labelpad=8)
    ax1.set_zlabel("Gate score g", fontsize=9, labelpad=6)
    ax1.set_title("3D gate score surface\n(budget=risk=1.0)", fontsize=10, pad=8)

    # ── Right panel: same data as 2D heatmap slices ──
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.set_facecolor("#F7F9FC")
    _pub_style(ax2)

    for trust_val, ls, marker, color in [
        (0.2, "--", "v", "#D55E00"),
        (0.5, "-.", "s", _OI["blue"]),
        (0.9, "-", "o", _OI["green"]),
    ]:
        scores = w_trust * trust_val + w_complete * C[:, 0]
        total_score = 0.60 + scores  # budget=risk=1.0
        ax2.plot(
            C[:, 0],
            total_score,
            label=f"trust={trust_val:.1f}",
            linestyle=ls,
            color=color,
            lw=2.2,
            marker=marker,
            markevery=10,
            markersize=5,
        )

    ax2.axhline(
        y=gate_exec,
        color="#0072B2",
        linestyle="--",
        lw=1.2,
        alpha=0.7,
        label=f"EXECUTE (g≥{gate_exec})",
    )
    ax2.axhline(
        y=gate_hold,
        color="#D55E00",
        linestyle=":",
        lw=1.2,
        alpha=0.7,
        label=f"HOLD (g≥{gate_hold})",
    )
    ax2.fill_between(C[:, 0], 0.60, gate_hold, alpha=0.06, color="#D55E00")
    ax2.fill_between(C[:, 0], gate_hold, gate_exec, alpha=0.06, color=_OI["yellow"])
    ax2.fill_between(C[:, 0], gate_exec, 1.0, alpha=0.06, color=_OI["green"])

    ax2.set_xlabel("Completeness score", fontsize=9)
    ax2.set_ylabel("Gate score g", fontsize=9)
    ax2.set_title("Score slices at fixed trust levels\n(budget=risk=1.0)", fontsize=10)
    ax2.legend(fontsize=7.5, loc="lower right", framealpha=0.85)
    ax2.set_ylim(0.55, 1.05)

    _add_provenance_note(fig)
    fig.tight_layout(pad=0.6, rect=(0, 0.035, 1, 1))
    _save(fig, "gate_score_3d.png")


# ── NEW: Figure — FEP–Colony Kernel correspondence ─────────────────────────


def fig_fep_correspondence() -> None:
    """Visual mapping of Free Energy Principle components to Colony Kernel
    subsystems. Used by 08_active_inference.md.

    A tiled table with color-coded rows showing the correspondence.
    """
    rows = [
        (
            "Generative model\np(o, s)",
            "PheromoneStore +\nConsequenceMemory",
            "Field stores accumulated\nconsequence history",
            _OI["blue"],
        ),
        (
            "Observations o",
            "Pheromone field:\nTraceField.sense()",
            "Signal strengths at\n(tick, location, type)",
            _OI["sky"],
        ),
        (
            "Hidden states s",
            "AgentTrustProfile:\ntrust_score, role",
            "Latent competence\ninferred from outcomes",
            _OI["orange"],
        ),
        (
            "Variational posterior\nq(s)",
            "RoleAdapter.infer_role()",
            "Deterministic mapping\nfrom trust→role",
            _OI["pink"],
        ),
        (
            "Expected Free Energy\nG(π)",
            "ActuationGate.evaluate()\ngate_score",
            "Cost of acting with\ncurrent belief state",
            _OI["vermil"],
        ),
        (
            "Policy π",
            "ActionProposal\n(action_type, target)",
            "Proposed course of\naction for gate",
            _OI["green"],
        ),
        (
            "Active inference\n(action selection)",
            "GateResult:\nEXECUTE/HOLD/REFUSE",
            "Score-thresholded\nternary decision",
            "#555555",
        ),
        (
            "Learning\n(parameter update)",
            "ConsequenceMemory.record()\ntrust_delta",
            "Trust deltas as\nparameter updates",
            _OI["pink"],
        ),
    ]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_facecolor("#F7F9FC")
    fig.patch.set_facecolor("#F7F9FC")
    ax.axis("off")

    col_widths = [0.22, 0.28, 0.32, 0.18]
    n_rows = len(rows)
    row_h = 0.65
    table_w = sum(col_widths)
    table_h = n_rows * row_h + 0.3

    # Headers
    headers = [
        "FEP component",
        "Colony Kernel\nsubsystem",
        "Formal\ncorrespondence",
        "Decay\nclass",
    ]
    x_positions = [sum(col_widths[:i]) for i in range(len(col_widths))]
    start_x = (1 - table_w) / 2
    start_y = 0.92

    for i, (header, x_pos) in enumerate(zip(headers, x_positions, strict=False)):
        ax.text(
            start_x + x_pos + col_widths[i] / 2,
            start_y,
            header,
            ha="center",
            va="center",
            fontsize=8.5,
            fontweight="bold",
            color="#1a1a1a",
        )

    # Rows
    for r, (fep, kernel, formal, color) in enumerate(rows):
        y = start_y - 0.08 - (r + 1) * row_h
        # Row background
        bg_color = "#EBF0F5" if r % 2 == 0 else "#F7F9FC"
        ax.add_patch(
            plt.Rectangle(
                (start_x, y),
                table_w,
                row_h,
                facecolor=bg_color,
                edgecolor="none",
                alpha=0.6,
                zorder=0,
            )
        )
        # Color stripe
        ax.add_patch(
            plt.Rectangle(
                (start_x, y),
                0.04,
                row_h,
                facecolor=color,
                edgecolor="none",
                alpha=0.9,
                zorder=1,
            )
        )
        # Cells
        texts = [fep, kernel, formal, ""]
        for j, (txt, x_pos, cw) in enumerate(
            zip(texts, x_positions, col_widths, strict=False)
        ):
            ax.text(
                start_x + x_pos + cw / 2,
                y + row_h / 2,
                txt,
                ha="center",
                va="center",
                fontsize=7.0 if j < 3 else 6.5,
                color="#1a1a1a",
                linespacing=1.2,
            )

    ax.set_title(
        "Free Energy Principle — Colony Kernel correspondence\n"
        "Each FEP component maps to a deterministic colony subsystem",
        fontsize=11,
        pad=6,
        color="#1a1a1a",
    )
    _add_provenance_note(fig)
    fig.tight_layout(pad=0.4, rect=(0, 0.035, 1, 1))
    _save(fig, "fep_correspondence.png")


# ── NEW: Figure — Gate formula approach comparison ─────────────────────────


def fig_formula_comparison() -> None:
    """Comparison of four gate formula approaches across 6 criteria.

    Used by 90_appendix_design_rationale.md §dr-gate-formula.
    Creates a grouped bar chart for visual comparison.
    """
    approaches = [
        "Weighted\nadditive",
        "Multiplicative",
        "Learned\nclassifier",
        "Rule\nsystem",
    ]
    criteria = [
        "Auditability",
        "Zero-shot\nvalidity",
        "Recovery\nsupport",
        "Calibration\ncost",
        "Interpretability",
        "Safety\nguarantees",
    ]
    # Scores: 5 = best, 1 = worst
    scores = np.array(
        [
            [5, 5, 4, 5, 5, 4],  # Weighted additive
            [3, 3, 2, 5, 3, 3],  # Multiplicative
            [1, 1, 3, 1, 1, 2],  # Learned classifier
            [4, 4, 1, 5, 4, 3],  # Rule system
        ]
    )

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_facecolor("#F7F9FC")
    fig.patch.set_facecolor("#F7F9FC")
    _pub_style(ax)

    n_criteria = len(criteria)
    n_approaches = len(approaches)
    bar_width = 0.18
    x = np.arange(n_criteria)
    colors = [_OI["green"], _OI["blue"], _OI["grey"], _OI["yellow"]]

    for i, (approach, color) in enumerate(zip(approaches, colors, strict=False)):
        offset = (i - n_approaches / 2 + 0.5) * bar_width
        bars = ax.bar(
            x + offset,
            scores[i],
            bar_width,
            label=approach.replace("\n", " "),
            color=color,
            alpha=0.85,
            edgecolor="white",
            linewidth=1.2,
            zorder=3,
        )
        # Annotate bars
        for bar, score in zip(bars, scores[i], strict=False):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                score + 0.08,
                str(score),
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
                color=color,
            )

    ax.set_xticks(x)
    ax.set_xticklabels(criteria, fontsize=8)
    ax.set_ylabel("Score (1–5)", fontsize=9)
    ax.set_ylim(0, 6.2)
    ax.legend(fontsize=8, loc="upper right", framealpha=0.88, ncol=2)
    ax.set_title(
        "Gate formula approach comparison across 6 criteria\n"
        "Weighted additive achieves the best combination of auditability, safety, and flexibility",
        fontsize=11,
        pad=10,
        color="#1a1a1a",
    )

    # Highlight additive column
    for i in range(n_criteria):
        max_score = scores[:, i].max()
        if scores[0, i] == max_score:
            ax.text(
                x[i],
                5.85,
                "← best",
                ha="center",
                va="bottom",
                fontsize=7.5,
                color=_OI["vermil"],
                fontweight="bold",
                style="italic",
            )

    _add_provenance_note(fig)
    fig.tight_layout(pad=0.4, rect=(0, 0.035, 1, 1))
    _save(fig, "formula_comparison.png")


# ── Main ───────────────────────────────────────────────────────────────────────


def main() -> None:
    print("Generating Codomyrmex manuscript figures...")
    fig_cover_art()
    fig_colony_pressure_loop()
    fig_pheromone_decay()
    fig_gate_score_heatmap()
    fig_trust_trajectory()
    fig_falsification_vectors()
    fig_subsystem_architecture()
    fig_gate_score_3d()
    fig_fep_correspondence()
    fig_formula_comparison()
    print(f"Done — 10 figures in {FIGDIR.relative_to(FIGDIR.parent.parent)}/")


if __name__ == "__main__":
    main()
