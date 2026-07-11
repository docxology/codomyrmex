"""Manuscript figure: gate score heatmap."""

from __future__ import annotations

from codomyrmex.manuscript.figures._common import (
    BoundaryNorm,
    ListedColormap,
    _add_provenance_note,
    _experiment_float,
    _gate_weight,
    _save,
    np,
    plt,
)


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
