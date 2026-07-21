"""Manuscript figure: pheromone decay."""

from __future__ import annotations

from codomyrmex.manuscript.figures._common import (
    _OI,
    _add_provenance_note,
    _experiment_float,
    _figure_parameter,
    _pub_style,
    _save,
    _var_float,
    _var_str,
    np,
    plt,
)


def fig_pheromone_decay() -> None:
    score_min = float(_figure_parameter("score_min", "CONFIG_SCORE_MIN", 0.0))
    score_max = float(_figure_parameter("score_max", "CONFIG_SCORE_MAX", 1.0))
    plot_horizon = float(
        _figure_parameter(
            "decay_plot_horizon_ticks",
            "CONFIG_DECAY_PLOT_HORIZON_TICKS",
            10,
        )
    )
    plot_points = int(
        _figure_parameter("decay_plot_points", "CONFIG_DECAY_PLOT_POINTS", 600, int)
    )
    t = np.linspace(score_min, plot_horizon, plot_points)
    base_rate = _experiment_float(
        "base_evaporation_rate", "CONFIG_BASE_EVAPORATION_RATE", 0.10
    )
    fast_mult = _var_float("CONFIG_DECAY_RATE_FAST", 3.0)
    normal_mult = _var_float("CONFIG_DECAY_RATE_NORMAL", 1.0)
    slow_mult = _var_float("CONFIG_DECAY_RATE_SLOW", 0.2)
    configs = [
        (
            f"FAST  (ε={base_rate * fast_mult:.2f}) — FAILURE, RISK",
            base_rate * fast_mult,
            _OI["vermil"],
            "solid",
            "FAST",
        ),
        (
            f"NORMAL (ε={base_rate * normal_mult:.2f}) — NEED, DEFAULT",
            base_rate * normal_mult,
            _OI["blue"],
            "dashed",
            "NORMAL",
        ),
        (
            f"SLOW  (ε={base_rate * slow_mult:.2f}) — SUCCESS, DEPENDENCY, PRIORITY",
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
        strength = np.maximum(score_min, score_max - rate * t)
        ax.plot(t, strength, label=label, color=color, linestyle=ls, lw=2.8, zorder=4)
        ax.fill_between(t, score_min, strength, color=color, alpha=0.07, zorder=2)
        ax.fill_between(
            t,
            score_min,
            np.minimum(strength, score_min + (score_max - score_min) / 2),
            color=color,
            alpha=0.05,
            zorder=2,
        )

        # Extinction marker for unit initial strength: ceil(1 / epsilon) ticks.
        tau = score_max / rate
        if tau <= plot_horizon:
            s_tau = score_min
            ax.vlines(
                tau,
                score_min,
                score_max,
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
        idx = int(min(score_max, 0.36) * len(t))
        y_lbl = strength[idx]
        if y_lbl > score_min + (score_max - score_min) * 0.02:
            offsets = {"FAST": -0.07, "NORMAL": 0.04, "SLOW": 0.025}
            ax.text(
                plot_horizon * 0.37,
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

    midpoint = score_min + (score_max - score_min) / 2
    midpoint_pct = (midpoint - score_min) / (score_max - score_min)
    ax.axhline(
        y=midpoint,
        color=_OI["grey"],
        linestyle="--",
        lw=1.2,
        alpha=0.55,
        label=f"{midpoint_pct:.0%} threshold",
    )
    ax.text(
        plot_horizon * 0.012,
        midpoint + (score_max - score_min) * 0.015,
        f"{midpoint_pct:.0%}",
        fontsize=8,
        color=_OI["grey"],
        va="bottom",
    )

    # FAST half-strength annotation for the linear recurrence.
    fast_rate = base_rate * fast_mult
    t_half = midpoint / fast_rate
    ax.annotate(
        f"FAST reaches {midpoint:.2f} at {t_half:.2f} ticks",
        xy=(t_half, midpoint),
        xytext=(t_half + plot_horizon * 0.065, score_max * 0.63),
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
    slow_per_tick = max(score_min, score_max - slow_rate)
    slow_retention = (slow_per_tick - score_min) / (score_max - score_min)
    slow_example_tick = _var_float("CONFIG_DECAY_REPORT_TICK", plot_horizon)
    slow_example_strength = max(score_min, score_max - slow_rate * slow_example_tick)
    slow_extinction = score_max / slow_rate
    ax.annotate(
        f"SLOW unit trace: {slow_retention:.0%} after one tick\n"
        f"(subtract {slow_rate:.2f}/tick; extinction at {slow_extinction:.0f} ticks)",
        xy=(slow_example_tick, slow_example_strength),
        xytext=(plot_horizon * 0.61, score_max * 0.68),
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
        f"s(t) = max({score_min:g}, s0 - epsilon t) for s0={score_max:g}\n"
        f"{_var_str('CONFIG_PARAMETER_STATUS_SHORT', 'Current default/illustrative decay rates')}",
        fontsize=11,
        pad=12,
    )
    ax.legend(fontsize=9, loc="upper right", framealpha=0.92, edgecolor="#CCCCCC")
    ax.set_xlim(score_min, plot_horizon)
    ax.set_ylim(score_min - score_max * 0.02, score_max * 1.10)
    _add_provenance_note(fig)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    _save(fig, "pheromone_decay.png")
