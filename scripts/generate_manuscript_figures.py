#!/usr/bin/env python3
"""Generate publication-quality figures for the Codomyrmex manuscript.

Outputs to output/figures/:
  cover.png                  — dark bioluminescent colony network (cover art)
  colony_pressure_loop.png   — 8-step feedback cycle (circular flow)
  pheromone_decay.png        — FAST/NORMAL/SLOW decay curves
  gate_score_heatmap.png     — gate decision landscape (trust × pressure)
  trust_trajectory.png       — agent trust score across outcomes
  falsification_vectors.png  — 10 adversarial attack vectors (lollipop)
  subsystem_architecture.png — Colony Control Plane (hexagonal star topology)
"""

from __future__ import annotations

import math
import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import ticker
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch, RegularPolygon

# ── Palettes ───────────────────────────────────────────────────────────────────

_OI: dict[str, str] = {
    "black":  "#000000",
    "orange": "#E69F00",
    "sky":    "#56B4E9",
    "green":  "#009E73",
    "yellow": "#F0E442",
    "blue":   "#0072B2",
    "vermil": "#D55E00",
    "pink":   "#CC79A7",
    "grey":   "#999999",
}

_COVER = {
    "bg":     "#060b14",
    "kernel": "#56B4E9",
    "phero":  "#E69F00",
    "ledger": "#0072B2",
    "gate":   "#D55E00",
    "memory": "#009E73",
    "role":   "#CC79A7",
    "prune":  "#778899",
    "falsif": "#C8C8D0",
    "spoke":  "#1E3A5F",
    "text":   "#E8EDF5",
    "dim":    "#7A8BA0",
    "grid":   "#0A1827",
}

DPI = 300
FIGDIR = Path(__file__).resolve().parent.parent / "output" / "figures"


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
    length = math.sqrt(dx ** 2 + dy ** 2) or 1.0
    p1 = (mid[0] - dy / length * curvature, mid[1] + dx / length * curvature)
    t = np.linspace(0, 1, n_pts)
    bx = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
    by = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
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
    ax.add_patch(plt.Circle((cx, cy), r_core, color=color, alpha=0.96, zorder=zorder + 1))


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
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(BG)
    ax.set_xlim(-W / 2, W / 2)
    ax.set_ylim(-H / 2, H / 2)
    ax.set_aspect("equal")
    ax.axis("off")

    subsystems = [
        ("PheromoneStore",      _COVER["phero"],  "Pheromone\nStore"),
        ("ResourceLedger",      _COVER["ledger"], "Resource\nLedger"),
        ("ActuationGate",       _COVER["gate"],   "Actuation\nGate"),
        ("ConsequenceMemory",   _COVER["memory"], "Consequence\nMemory"),
        ("RoleAdapter",         _COVER["role"],   "Role\nAdapter"),
        ("PruningDaemon",       _COVER["prune"],  "Pruning\nDaemon"),
        ("FalsificationWorker", _COVER["falsif"], "Falsification\nWorker"),
    ]
    n_sub = len(subsystems)
    R_sub   = 2.2
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
                ax.add_patch(RegularPolygon(
                    (hx, hy), numVertices=6, radius=0.28, orientation=0,
                    fill=False, edgecolor=_COVER["grid"],
                    linewidth=0.30, alpha=0.50, zorder=0,
                ))

    # Background radial glow
    for k in range(24, 0, -1):
        r = 0.12 + k * 0.19
        ax.add_patch(plt.Circle((CX, CY), r, color=_COVER["kernel"],
                                alpha=0.018 * (1 - k / 26), zorder=0))

    # Orbital ring
    theta = np.linspace(0, 2 * math.pi, 300)
    ax.plot(R_sub * np.cos(theta), R_sub * np.sin(theta),
            color="#1A2E42", lw=0.55, alpha=0.55, zorder=1)

    # Ghostly spokes
    for i, (_, color, _) in enumerate(subsystems):
        ax.plot([CX, sx[i]], [CY, sy[i]], color=color,
                alpha=0.09, lw=0.55, zorder=1, linestyle="--")

    # Pheromone trails + particles
    n_particles = 11
    for i, (_, color, _) in enumerate(subsystems):
        bx, by = _bezier((sx[i], sy[i]), (CX, CY), curvature=0.38, n_pts=150)
        for seg in range(0, len(bx) - 4, 4):
            frac = seg / len(bx)
            ax.plot(bx[seg:seg + 5], by[seg:seg + 5],
                    color=color, alpha=0.08 + frac * 0.28, lw=0.85, zorder=2)
        bx2, by2 = _bezier((CX, CY), (sx[i], sy[i]), curvature=-0.20, n_pts=150)
        ax.plot(bx2, by2, color=color, alpha=0.09, lw=0.40, zorder=2, linestyle=":")
        for j in range(n_particles):
            frac = 0.05 + j * (0.90 / (n_particles - 1))
            idx = int(frac * (len(bx) - 1))
            ax.scatter(bx[idx], by[idx], color=color,
                       s=5 + j * 9, alpha=0.65 + j * 0.03, zorder=4, linewidths=0)

    # Outer agent ring (18 agents)
    n_agents = 18
    for k in range(n_agents):
        ag_a = 2 * math.pi * k / n_agents
        ax_pos = R_outer * math.cos(ag_a)
        ay_pos = R_outer * math.sin(ag_a)
        dists = [math.sqrt((ax_pos - sx[j]) ** 2 + (ay_pos - sy[j]) ** 2)
                 for j in range(n_sub)]
        nearest = int(np.argmin(dists))
        ag_color = subsystems[nearest][1]
        ax.plot([ax_pos, sx[nearest]], [ay_pos, sy[nearest]],
                color=ag_color, alpha=0.07, lw=0.28, zorder=1)
        _glow(ax, ax_pos, ay_pos, ag_color,
              r_core=0.038, r_max=0.13, n_rings=6, alpha_peak=0.22, zorder=3)

    # Subsystem nodes
    for i, (_, color, short) in enumerate(subsystems):
        _glow(ax, sx[i], sy[i], color,
              r_core=0.23, r_max=0.68, n_rings=13, alpha_peak=0.17, zorder=5)
        lx = R_label * math.cos(angles[i])
        ly = R_label * math.sin(angles[i])
        ax.text(lx, ly, short, fontsize=6.5, color=color,
                ha="center", va="center", fontweight="bold", zorder=7,
                linespacing=1.4)

    # ColonyKernel hub
    _glow(ax, CX, CY, _COVER["kernel"],
          r_core=0.34, r_max=0.98, n_rings=16, alpha_peak=0.21, zorder=6)
    ax.text(CX, CY + 0.11, "Colony", fontsize=11, color="white",
            ha="center", va="center", fontweight="bold", zorder=9,
            fontfamily="monospace")
    ax.text(CX, CY - 0.21, "Kernel", fontsize=11, color="white",
            ha="center", va="center", fontweight="bold", zorder=9,
            fontfamily="monospace")

    # Title
    ax.text(0, H / 2 - 0.24, "C O D O M Y R M E X",
            fontsize=22, color=_COVER["text"], ha="center", va="top",
            fontweight="bold", zorder=10, fontfamily="monospace")
    ax.plot([-2.6, 2.6], [H / 2 - 0.62, H / 2 - 0.62],
            color=_COVER["dim"], lw=0.75, alpha=0.50, zorder=10)
    ax.text(0, H / 2 - 0.79,
            "An Artificial Ecology for Agentic Software Development",
            fontsize=9, color=_COVER["dim"], ha="center", va="top",
            zorder=10, style="italic")
    ax.text(-W / 2 + 0.14, -H / 2 + 0.14,
            "Colony Control Plane  ·  Stigmergic Pressure  ·  Falsification-Gated Actuation",
            fontsize=6, color=_COVER["dim"], ha="left", va="bottom", zorder=10)

    _save(fig, "cover.png")


# ── Figure 1 — Colony pressure loop ───────────────────────────────────────────

def fig_colony_pressure_loop() -> None:
    steps = [
        ("Environmental\nPressure",  _OI["orange"], "1"),
        ("Proposal\nSubmission",     _OI["sky"],    "2"),
        ("Actuation\nGate",          _OI["vermil"], "3"),
        ("Action\nExecution",        _OI["blue"],   "4"),
        ("Consequence\nRecord",      _OI["green"],  "5"),
        ("Trust &\nRole Update",     _OI["pink"],   "6"),
        ("Falsification\nReview",    "#555555",     "7"),
        ("Pheromone\nDeposit",       _OI["orange"], "8"),
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
        ax.plot(ring_r * np.cos(theta), ring_r * np.sin(theta),
                color="#D0E4F0", lw=0.55, alpha=0.80, zorder=0)

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
        ax.add_patch(FancyBboxPatch(
            (cx[i] - box_w / 2 + 0.05, cy[i] - box_h / 2 - 0.05),
            box_w, box_h, boxstyle="round,pad=0.12",
            facecolor="#000000", alpha=0.10, linewidth=0, zorder=2,
        ))
        # Box
        ax.add_patch(FancyBboxPatch(
            (cx[i] - box_w / 2, cy[i] - box_h / 2),
            box_w, box_h, boxstyle="round,pad=0.12",
            facecolor=color, edgecolor="white", linewidth=2.5, zorder=3,
        ))
        text_color = "white" if color not in (_OI["yellow"], _OI["orange"]) else "#1a1a1a"
        ax.text(cx[i], cy[i] + 0.04, label,
                ha="center", va="center",
                fontsize=8.5, fontweight="bold", color=text_color, zorder=4,
                linespacing=1.25)
        # Circular step badge
        badge_cx = cx[i] - box_w / 2 + 0.17
        badge_cy = cy[i] + box_h / 2 - 0.11
        ax.add_patch(plt.Circle((badge_cx, badge_cy), 0.11,
                                color="white", alpha=0.88, zorder=5))
        ax.text(badge_cx, badge_cy, step_n, ha="center", va="center",
                fontsize=7.5, fontweight="bold", color=color, zorder=6)

    # Hub with glow rings
    for ring_r, alpha in [(0.98, 0.07), (0.78, 0.13), (0.56, 0.20)]:
        ax.add_patch(plt.Circle((0, 0), ring_r, facecolor=_OI["sky"],
                                edgecolor="none", alpha=alpha, zorder=3))
    ax.add_patch(plt.Circle((0, 0), 0.70, facecolor=_OI["sky"],
                             edgecolor="white", linewidth=2.5, alpha=0.97, zorder=4))
    ax.text(0, 0.14, "Colony", ha="center", va="center",
            fontsize=10, fontweight="bold", color="white", zorder=6)
    ax.text(0, -0.12, "Control", ha="center", va="center",
            fontsize=8.5, color="white", alpha=0.90, zorder=6)
    ax.text(0, -0.34, "Plane", ha="center", va="center",
            fontsize=8.5, color="white", alpha=0.90, zorder=6)

    ax.set_title(
        "Colony feedback loop — 8-step circular actuation cycle\n"
        "Each proposal traverses the full ring before state is committed",
        fontsize=11, pad=16, color="#1a1a1a",
    )
    fig.tight_layout(pad=0.4)
    _save(fig, "colony_pressure_loop.png")


# ── Figure 2 — Pheromone decay curves ─────────────────────────────────────────

def fig_pheromone_decay() -> None:
    t = np.linspace(0, 10, 600)
    configs = [
        ("FAST  (λ=3.0) — FAILURE, RISK",    3.0, _OI["vermil"], "solid",  "FAST"),
        ("NORMAL (λ=1.0) — NEED, DEPENDENCY", 1.0, _OI["blue"],   "dashed", "NORMAL"),
        ("SLOW  (λ=0.2) — SUCCESS, PRIORITY", 0.2, _OI["green"],  "dotted", "SLOW"),
    ]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.set_facecolor("#F7F9FC")
    fig.patch.set_facecolor("#F7F9FC")
    _pub_style(ax)

    for label, rate, color, ls, cls_name in configs:
        strength = np.exp(-rate * t)
        ax.plot(t, strength, label=label, color=color, linestyle=ls, lw=2.8, zorder=4)
        ax.fill_between(t, 0, strength, color=color, alpha=0.07, zorder=2)
        ax.fill_between(t, 0, np.minimum(strength, 0.50), color=color, alpha=0.05, zorder=2)

        # Time-constant marker (τ = 1/λ), value = 1/e ≈ 0.368
        tau = 1.0 / rate
        if tau <= 10.0:
            s_tau = math.exp(-1.0)  # always 1/e
            ax.vlines(tau, 0, s_tau, colors=color, linestyles=":", lw=1.0, alpha=0.50, zorder=3)
            ax.hlines(s_tau, 0, tau, colors=color, linestyles=":", lw=1.0, alpha=0.50, zorder=3)
            ax.scatter([tau], [s_tau], color=color, s=60, zorder=5,
                       edgecolors="white", linewidths=1.2)

        # Curve label (direct)
        idx = int(3.6 / 10.0 * len(t))
        y_lbl = strength[idx]
        if y_lbl > 0.02:
            offsets = {"FAST": -0.07, "NORMAL": 0.04, "SLOW": 0.025}
            ax.text(3.7, y_lbl + offsets[cls_name], cls_name,
                    fontsize=9, color=color, fontweight="bold", va="center",
                    bbox={"boxstyle": "round,pad=0.20", "facecolor": "white",
                              "edgecolor": color, "alpha": 0.88, "linewidth": 1.0})

    # 50% line
    ax.axhline(y=0.5, color=_OI["grey"], linestyle="--", lw=1.2, alpha=0.55,
               label="50% threshold")
    ax.text(0.12, 0.515, "50%", fontsize=8, color=_OI["grey"], va="bottom")

    # FAST half-life annotation
    t_half = math.log(2) / 3.0
    ax.annotate(
        f"FAST t½ = {t_half:.2f} ticks",
        xy=(t_half, 0.5), xytext=(t_half + 0.65, 0.63),
        arrowprops={"arrowstyle": "->", "color": _OI["vermil"], "lw": 1.1},
        fontsize=8.5, color=_OI["vermil"],
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white",
                  "edgecolor": _OI["vermil"], "alpha": 0.90},
    )

    # SLOW per-tick retention (corrected — per-tick, not 10-tick cumulative)
    slow_per_tick = math.exp(-0.2)  # ≈ 0.819
    ax.annotate(
        f"SLOW: {slow_per_tick:.0%} retained per tick\n"
        r"($e^{-0.2} \approx 0.819$; τ = 5 ticks)",
        xy=(5.0, slow_per_tick), xytext=(5.5, 0.93),
        arrowprops={"arrowstyle": "->", "color": _OI["green"], "lw": 1.1},
        fontsize=8.0, color=_OI["green"], ha="center",
        bbox={"boxstyle": "round,pad=0.28", "facecolor": "white",
                  "edgecolor": _OI["green"], "alpha": 0.90},
    )

    ax.set_xlabel("Ticks since deposit", fontsize=11.5, color="#333333")
    ax.set_ylabel("Pheromone signal strength (normalised)", fontsize=11.5, color="#333333")
    ax.set_title(
        "Pheromone signal decay by rate class\n"
        r"$s(t) = s_0 \cdot e^{-\lambda t}$  —  three rate classes map to signal volatility",
        fontsize=11, pad=12,
    )
    ax.legend(fontsize=9, loc="upper right", framealpha=0.92, edgecolor="#CCCCCC")
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.02, 1.10)
    fig.tight_layout()
    _save(fig, "pheromone_decay.png")


# ── Figure 3 — Gate score heatmap ─────────────────────────────────────────────

def fig_gate_score_heatmap() -> None:
    N = 160
    trust_vals   = np.linspace(0.0, 1.0, N)
    pressure_vals = np.linspace(0.0, 10.0, N)
    T, P = np.meshgrid(trust_vals, pressure_vals)

    risk_ok = np.where(P < 3.0, 1.0, np.where(P < 6.0, 0.5, 0.0))
    score   = 0.30 * np.ones_like(T) + 0.30 * risk_ok + 0.25 * np.clip(T, 0, 1) + 0.15
    score   = np.where(T < 0.10, 0.0, score)

    # Tri-zone colormap: deep red → amber → green
    cmap = LinearSegmentedColormap.from_list(
        "gate",
        [(0.00, "#6B0000"), (0.28, "#C0392B"), (0.46, "#E67E22"),
         (0.50, "#F5CE6A"), (0.60, "#27AE60"), (1.00, "#0A5C36")],
        N=512,
    )

    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    ax.set_facecolor("#080808")
    fig.patch.set_facecolor("#F7F9FC")

    im = ax.pcolormesh(trust_vals, pressure_vals, score,
                       cmap=cmap, vmin=0.0, vmax=1.0, shading="gouraud")

    cbar = fig.colorbar(im, ax=ax, pad=0.02, shrink=0.96)
    cbar.ax.tick_params(labelsize=9)
    cbar.set_label("Gate score", fontsize=10)

    # Boundary contours
    cs = ax.contour(trust_vals, pressure_vals, score,
                    levels=[0.50, 0.75],
                    colors=["#FFE066", "white"],
                    linestyles=["--", "-"],
                    linewidths=[2.0, 2.5])
    ax.clabel(cs, fmt={0.50: "HOLD ≥ 0.50", 0.75: "EXECUTE ≥ 0.75"},
              fontsize=9.5, inline=True, inline_spacing=6)

    # SANDBOX zone
    ax.axvspan(0.0, 0.10, alpha=0.62, color="#000000", zorder=2)
    ax.text(0.05, 9.2, "SANDBOX\n(override)", fontsize=7.5, color="white",
            ha="center", va="top", fontweight="bold", zorder=3)

    # Decision region labels
    ax.text(0.88, 1.2,  "EXECUTE", fontsize=12, color="white",
            fontweight="bold", ha="center", va="center", zorder=3, alpha=0.90)
    ax.text(0.65, 5.8,  "HOLD",    fontsize=12, color="white",
            fontweight="bold", ha="center", va="center", zorder=3, alpha=0.90)
    ax.text(0.22, 8.3,  "REFUSE",  fontsize=12, color="white",
            fontweight="bold", ha="center", va="center", zorder=3, alpha=0.90)

    # Trust threshold verticals
    for x_val, label_txt in [(0.30, "hard\nfloor"), (0.65, "promote")]:
        ax.axvline(x=x_val, color="white", lw=0.8, alpha=0.35, linestyle=":")
        ax.text(x_val, 0.30, f"{x_val}\n{label_txt}", fontsize=7,
                color="white", ha="center", alpha=0.80, zorder=3, va="bottom")

    # Annotated example points (hardcoded from canonical formula)
    # GUARD_ANT: trust=0.90, P=1.0 → risk_ok=1.0, score=0.30+0.30+0.225+0.15=0.975
    # moderate: trust=0.40, P=5.5 → risk_ok=0.5, score=0.30+0.15+0.10+0.15=0.70
    # low trust: trust=0.15, P=7.5 → risk_ok=0.0, score=0.30+0+0.0375+0.15=0.49
    examples = [
        (0.90, 1.0, "GUARD_ANT\nfull spec", "white",   "EXECUTE", "0.98"),
        (0.40, 5.5, "moderate\nrisk",       "#FFE066", "HOLD",    "0.70"),
        (0.15, 7.5, "low trust\nhigh risk", "#FF9999", "REFUSE",  "0.49"),
    ]
    for tx, tp, desc, ecolor, decision, sc in examples:
        ax.scatter([tx], [tp], color=ecolor, s=115, zorder=6,
                   edgecolors="white", linewidths=1.8)
        ax.annotate(
            f"{desc}\nscore={sc} → {decision}",
            xy=(tx, tp), xytext=(tx + 0.13, tp + 0.9),
            fontsize=7, color=ecolor,
            bbox={"boxstyle": "round,pad=0.22", "facecolor": "#00000099",
                      "edgecolor": ecolor, "alpha": 0.92},
        )

    ax.set_xlabel("Agent trust score", fontsize=11.5)
    ax.set_ylabel("Combined pheromone pressure (RISK + 0.5 × FAILURE)", fontsize=11.5)
    ax.set_title(
        "Gate decision landscape\n"
        "score = 0.30·budget + 0.30·risk_ok + 0.25·trust_ok + 0.15·completeness\n"
        "(budget=1.0, completeness=1.0; SANDBOX zone forces score=0 when trust < 0.10)",
        fontsize=9.5, pad=10,
    )
    ax.tick_params(labelsize=9.5)
    fig.tight_layout()
    _save(fig, "gate_score_heatmap.png")


# ── Figure 4 — Trust trajectory ───────────────────────────────────────────────

def fig_trust_trajectory() -> None:
    trust_init = 0.10
    delta      = 0.04
    # Outcomes 0–12 (the manuscript window)
    outcomes = list(range(13))
    trust    = [min(trust_init + i * delta, 1.0) for i in outcomes]

    def _role(tv: float) -> str:
        if tv < 0.30:
            return "SANDBOX"
        if tv < 0.65:
            return "REPAIR_ANT"
        return "DISPATCHER"

    roles     = [_role(tv) for tv in trust]
    sandbox_c = _OI["orange"]
    repair_c  = _OI["green"]
    disp_c    = _OI["blue"]
    role_col  = {"SANDBOX": sandbox_c, "REPAIR_ANT": repair_c, "DISPATCHER": disp_c}
    col_pts   = [role_col[r] for r in roles]

    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    ax.set_facecolor("#F7F9FC")
    fig.patch.set_facecolor("#F7F9FC")
    _pub_style(ax)

    repair_idx = next((i for i, r in enumerate(roles) if r == "REPAIR_ANT"), None)
    sandbox_end = (repair_idx - 0.5) if repair_idx is not None else 12.5

    # Zone shading
    ax.axvspan(-0.5, sandbox_end, alpha=0.09, color=sandbox_c)
    ax.axvspan(sandbox_end, 12.5, alpha=0.07, color=repair_c)
    ax.axhspan(0.65, 0.82, alpha=0.04, color=disp_c)

    # Zone labels
    sandbox_mid = sandbox_end / 2 if repair_idx else 6.0
    ax.text(sandbox_mid, 0.045, "SANDBOX ZONE", ha="center", va="bottom",
            fontsize=8.5, color=sandbox_c, alpha=0.85, fontweight="bold")
    ax.text(sandbox_mid, 0.020, "(all proposals refused)", ha="center", va="bottom",
            fontsize=7, color=sandbox_c, alpha=0.65)
    repair_mid = (sandbox_end + 12.5) / 2
    ax.text(repair_mid, 0.045, "REPAIR_ANT ZONE", ha="center", va="bottom",
            fontsize=8.5, color=repair_c, alpha=0.85, fontweight="bold")
    ax.text(repair_mid, 0.020, "(gate evaluated)", ha="center", va="bottom",
            fontsize=7, color=repair_c, alpha=0.65)

    # Thresholds
    ax.axhline(y=0.10, color=_OI["grey"],  linestyle=":", lw=1.2, alpha=0.55,
               label="Entry floor (0.10)")
    ax.axhline(y=0.30, color=sandbox_c,    linestyle=":", lw=1.8, alpha=0.85,
               label="REPAIR_ANT floor (0.30)")
    ax.axhline(y=0.65, color=disp_c,       linestyle="--", lw=1.8, alpha=0.80,
               label="DISPATCHER threshold (0.65)")
    for yval, color in [(0.30, sandbox_c), (0.65, disp_c)]:
        ax.text(-0.48, yval + 0.008, f"{yval:.2f}", fontsize=7.5,
                color=color, va="bottom", alpha=0.88)

    # Gradient line (segment per role)
    for i in range(len(outcomes) - 1):
        seg_color = col_pts[i]
        ax.plot(outcomes[i:i + 2], trust[i:i + 2],
                color=seg_color, lw=2.9, zorder=3, solid_capstyle="round")
        ax.fill_between(outcomes[i:i + 2], trust_init - 0.01, trust[i:i + 2],
                        color=seg_color, alpha=0.08, zorder=2)

    # Projected future trajectory (dashed, up to outcome 26)
    future_outcomes = list(range(12, 28))
    future_trust = [min(trust_init + i * delta, 1.0) for i in future_outcomes]
    ax.plot(future_outcomes, future_trust, color=disp_c,
            lw=1.8, linestyle="--", alpha=0.40, zorder=2)
    disp_outcome = next(
        (i for i in future_outcomes if min(trust_init + i * delta, 1.0) >= 0.65), None
    )
    if disp_outcome is not None:
        ax.scatter([disp_outcome], [0.65], color=disp_c,
                   s=90, alpha=0.45, zorder=3, edgecolors="white", linewidths=1.2)
        ax.text(disp_outcome + 0.2, 0.67, f"~outcome {disp_outcome}\nDISPATCHER",
                fontsize=7, color=disp_c, alpha=0.60, va="bottom")

    # Scatter
    ax.scatter(outcomes, trust, c=col_pts, s=150, zorder=6,
               edgecolors="white", linewidths=1.5)

    # Checkpoint labels
    for idx in [0, 3, 6, 9, 12]:
        if idx < len(trust):
            ax.text(idx, trust[idx] + 0.025, f"{trust[idx]:.2f}",
                    ha="center", va="bottom", fontsize=8.5, color="#222222",
                    fontweight="bold")

    # Graduation annotation
    if repair_idx is not None:
        ax.annotate(
            f"Outcome {repair_idx}: SANDBOX → REPAIR_ANT\n"
            f"(trust = {trust[repair_idx]:.2f} ≥ 0.30)",
            xy=(repair_idx, trust[repair_idx]),
            xytext=(repair_idx + 2.2, trust[repair_idx] - 0.075),
            arrowprops={"arrowstyle": "-|>", "color": repair_c, "lw": 1.5},
            fontsize=8.5, color=repair_c, fontweight="bold",
            bbox={"boxstyle": "round,pad=0.35", "facecolor": "white",
                      "edgecolor": repair_c, "alpha": 0.92, "linewidth": 1.5},
        )

    # Legend
    legend_items = [
        mpatches.Patch(color=sandbox_c, label="SANDBOX (trust < 0.30)"),
        mpatches.Patch(color=repair_c,  label="REPAIR_ANT (0.30–0.65)"),
        mpatches.Patch(color=disp_c,    label="DISPATCHER (≥ 0.65, projected)"),
        plt.Line2D([], [], color=_OI["grey"],  linestyle=":", lw=1.5, label="Entry floor (0.10)"),
        plt.Line2D([], [], color=sandbox_c,    linestyle=":", lw=1.5, label="Hard floor (0.30)"),
        plt.Line2D([], [], color=disp_c,       linestyle="--", lw=1.5, label="DISPATCHER thr. (0.65)"),
    ]
    ax.legend(handles=legend_items, fontsize=8, loc="upper left",
              ncol=2, framealpha=0.92, edgecolor="#CCCCCC")

    ax.set_xlabel("Outcome number (consecutive successful passes)", fontsize=11.5)
    ax.set_ylabel("Agent trust score", fontsize=11.5)
    trust_at_12 = trust_init + 12 * delta
    ax.set_title(
        "Trust trajectory — conservative model (Δ = 0.04 per pass)\n"
        f"trust {trust_init:.2f} → {trust_at_12:.2f} after 12 outcomes; "
        "dashed projection shows DISPATCHER crossing",
        fontsize=10.5, pad=12,
    )
    ax.set_xlim(-0.5, 27)
    ax.set_ylim(0.0, 0.84)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.tick_params(labelsize=9.5)
    fig.tight_layout()
    _save(fig, "trust_trajectory.png")


# ── Figure 5 — Falsification vectors (lollipop) ───────────────────────────────

def fig_falsification_vectors() -> None:
    vectors = [
        ("SECURITY_RISK",           "CRITICAL", _OI["black"]),
        ("NO_ROLLBACK",             "HIGH",     _OI["vermil"]),
        ("FALSE_METRIC",            "HIGH",     _OI["vermil"]),
        ("HIDDEN_MAINTENANCE_COST", "HIGH",     _OI["vermil"]),
        ("NO_TEST_VALUE",           "HIGH",     _OI["vermil"]),
        ("SCOPE_CREEP",             "MEDIUM",   _OI["orange"]),
        ("CIRCULAR_DEPS",           "MEDIUM",   _OI["orange"]),
        ("DEPENDENCY_RISK",         "MEDIUM",   _OI["orange"]),
        ("OVER_BROAD_MODULE",       "LOW",      _OI["sky"]),
        ("PREMATURE_ABSTRACTION",   "LOW",      _OI["sky"]),
    ]
    sev_weight = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    names   = [v[0] for v in vectors]
    weights = [sev_weight[v[1]] for v in vectors]
    colors  = [v[2] for v in vectors]
    labels  = [v[1] for v in vectors]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.set_facecolor("#F7F9FC")
    fig.patch.set_facecolor("#F7F9FC")
    _pub_style(ax)

    y_pos = list(range(len(names)))

    # Severity band backgrounds
    for x0, x1, bcolor, balpha in [
        (3.5, 4.55, _OI["black"],  0.06),
        (2.5, 3.5,  _OI["vermil"], 0.05),
        (1.5, 2.5,  _OI["orange"], 0.04),
        (0.5, 1.5,  _OI["sky"],    0.04),
    ]:
        ax.axvspan(x0, x1, alpha=balpha, color=bcolor, zorder=0)

    # Lollipop stems
    for i, (w, color) in enumerate(zip(weights, colors, strict=False)):
        ax.plot([0, w], [y_pos[i], y_pos[i]], color=color,
                lw=2.0, alpha=0.55, zorder=2, solid_capstyle="round")

    # Lollipop heads
    ax.scatter(weights, y_pos, c=colors, s=220, zorder=4,
               edgecolors="white", linewidths=2.0)

    # Severity letter inside head
    for i, (w, sev, color) in enumerate(zip(weights, labels, colors, strict=False)):
        txt_color = "white" if color not in (_OI["sky"], _OI["yellow"]) else "#1a1a1a"
        ax.text(w, y_pos[i], sev[0],  # C / H / M / L
                va="center", ha="center",
                fontsize=7.5, color=txt_color, fontweight="bold", zorder=5)

    # CRITICAL callout
    ax.annotate(
        "Unconditional REFUSE\nbefore gate scoring",
        xy=(4.0, 0), xytext=(3.35, 1.15),
        arrowprops={"arrowstyle": "-|>", "color": "#333333", "lw": 1.2},
        fontsize=8.5, color="#333333", ha="center",
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "#FFF0EE",
                  "edgecolor": _OI["vermil"], "alpha": 0.95, "linewidth": 1.5},
    )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=9, fontfamily="monospace")
    ax.set_xlabel("Severity weight", fontsize=11.5, color="#333333")
    ax.set_xticks([1, 2, 3, 4])
    ax.set_xticklabels(["LOW (1)", "MEDIUM (2)", "HIGH (3)", "CRITICAL (4)"],
                       fontsize=9.5)
    ax.set_title(
        "FalsificationWorker — 10 adversarial attack vectors\n"
        "Any CRITICAL finding issues an unconditional REFUSE before gate scoring",
        fontsize=11, pad=12,
    )

    legend_items = [
        mpatches.Patch(color=_OI["black"],  label="CRITICAL — unconditional REFUSE"),
        mpatches.Patch(color=_OI["vermil"], label="HIGH — strong REFUSE signal"),
        mpatches.Patch(color=_OI["orange"], label="MEDIUM — HOLD candidate"),
        mpatches.Patch(color=_OI["sky"],    label="LOW — advisory"),
    ]
    ax.legend(handles=legend_items, fontsize=8.5, loc="lower right",
              framealpha=0.92, ncol=2, edgecolor="#CCCCCC")

    ax.invert_yaxis()
    ax.set_xlim(0, 4.7)
    fig.tight_layout()
    _save(fig, "falsification_vectors.png")


# ── Figure 6 — Subsystem architecture (hexagonal star) ────────────────────────

def fig_subsystem_architecture() -> None:
    subsystems = [
        ("PheromoneStore",      _OI["orange"], "Stigmergic\ntraces & decay"),
        ("ResourceLedger",      _OI["blue"],   "Budget\nenforcement"),
        ("ActuationGate",       _OI["vermil"], "Permission\nscoring gate"),
        ("ConsequenceMemory",   _OI["green"],  "SQLite\noutcome log"),
        ("RoleAdapter",         _OI["pink"],   "Trust → role\ninference"),
        ("PruningDaemon",       _OI["grey"],   "Stale module\neviction"),
        ("FalsificationWorker", "#444444",     "Adversarial\npre-check"),
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
        ax.plot(ring_r * np.cos(theta), ring_r * np.sin(theta),
                color="#CCD8E8", lw=0.55, alpha=0.60, zorder=0)

    # Spokes: outbound arrow only, plus thin return line
    for i, (name, color, subtitle) in enumerate(subsystems):
        ax.plot([cx[i] * 0.32, cx[i] * 0.84], [cy[i] * 0.32, cy[i] * 0.84],
                color=color, alpha=0.20, lw=1.8, zorder=1)
        ax.annotate(
            "",
            xy=(cx[i] * 0.86, cy[i] * 0.86),
            xytext=(cx[i] * 0.32, cy[i] * 0.32),
            arrowprops={"arrowstyle": "-|>", "color": color,
                            "alpha": 0.55, "lw": 1.5, "mutation_scale": 12},
            zorder=2,
        )
        # Thin return (kernel ← subsystem)
        ax.annotate(
            "",
            xy=(cx[i] * 0.35, cy[i] * 0.35),
            xytext=(cx[i] * 0.74, cy[i] * 0.74),
            arrowprops={"arrowstyle": "-|>", "color": _OI["sky"],
                            "alpha": 0.28, "lw": 0.85, "mutation_scale": 9},
            zorder=1,
        )

    # Hexagonal subsystem nodes
    hex_r = 0.60
    for i, (name, color, subtitle) in enumerate(subsystems):
        # Shadow
        ax.add_patch(RegularPolygon(
            (cx[i] + 0.06, cy[i] - 0.06), numVertices=6, radius=hex_r,
            orientation=0, facecolor="#000000", alpha=0.09, edgecolor="none", zorder=2,
        ))
        # Main hex
        ax.add_patch(RegularPolygon(
            (cx[i], cy[i]), numVertices=6, radius=hex_r,
            orientation=0, facecolor=color, edgecolor="white",
            linewidth=2.2, zorder=3,
        ))
        text_color = "white" if color != _OI["yellow"] else "#1a1a1a"
        ax.text(cx[i], cy[i] + 0.16, name,
                ha="center", va="center",
                fontsize=7.5, fontweight="bold", color=text_color, zorder=5)
        ax.text(cx[i], cy[i] - 0.20, subtitle,
                ha="center", va="center",
                fontsize=6.5, color=text_color, alpha=0.88, zorder=5,
                linespacing=1.3)

    # Centre hexagonal hub (ColonyKernel) with glow rings
    for glow_r, galpha in [(1.22, 0.06), (0.98, 0.10), (0.80, 0.17)]:
        ax.add_patch(RegularPolygon(
            (0, 0), numVertices=6, radius=glow_r, orientation=0,
            facecolor=_OI["sky"], edgecolor="none", alpha=galpha, zorder=2,
        ))
    ax.add_patch(RegularPolygon(
        (0, 0), numVertices=6, radius=0.76, orientation=0,
        facecolor=_OI["sky"], edgecolor="white", linewidth=2.8, alpha=0.97, zorder=4,
    ))
    ax.text(0, 0.14, "Colony", ha="center", va="center",
            fontsize=12.5, fontweight="bold", color="white", zorder=6)
    ax.text(0, -0.16, "Kernel", ha="center", va="center",
            fontsize=12.5, fontweight="bold", color="white", zorder=6)

    ax.set_title(
        "Colony Control Plane — star topology with hexagonal subsystem nodes\n"
        "ColonyKernel owns all subsystem state; subsystems communicate only via models.py",
        fontsize=11, pad=14, color="#1a1a1a",
    )
    fig.tight_layout(pad=0.4)
    _save(fig, "subsystem_architecture.png")


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
    print(f"Done — 7 figures in {FIGDIR.relative_to(FIGDIR.parent.parent)}/")


if __name__ == "__main__":
    main()
