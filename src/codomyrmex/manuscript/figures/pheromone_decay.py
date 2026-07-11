"""Manuscript figure: pheromone decay."""

from __future__ import annotations

from codomyrmex.manuscript.figures._common import (
    _OI,
    _add_provenance_note,
    _experiment_float,
    _pub_style,
    _save,
    _var_float,
    math,
    np,
    plt,
)


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
