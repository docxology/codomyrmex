"""Manuscript figure: gate score heatmap."""

from __future__ import annotations

from codomyrmex.manuscript.figures._common import (
    BoundaryNorm,
    ListedColormap,
    _add_provenance_note,
    _experiment_float,
    _figure_parameter,
    _gate_weight,
    _save,
    _var_float,
    _var_str,
    np,
    plt,
)


def fig_gate_score_heatmap() -> None:
    score_min = float(_figure_parameter("score_min", "CONFIG_SCORE_MIN", 0.0))
    score_max = float(_figure_parameter("score_max", "CONFIG_SCORE_MAX", 1.0))
    grid_points = int(
        _figure_parameter("heatmap_grid_points", "CONFIG_HEATMAP_GRID_POINTS", 160, int)
    )
    pressure_max = float(
        _figure_parameter("heatmap_pressure_max", "CONFIG_HEATMAP_PRESSURE_MAX", 10.0)
    )
    trust_vals = np.linspace(score_min, score_max, grid_points)
    pressure_vals = np.linspace(score_min, pressure_max, grid_points)
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
    trust_full_credit = _experiment_float(
        "trust_full_credit_threshold", "CONFIG_TRUST_FULL_CREDIT_THRESHOLD", 0.60
    )
    medium_hazard = _var_float("CONFIG_HAZARD_MEDIUM_THRESHOLD", 3.0)
    high_hazard = _var_float("CONFIG_HAZARD_HIGH_THRESHOLD", 6.0)
    risk_credit_medium = _var_float("CONFIG_RISK_CREDIT_MEDIUM", 0.5)

    risk_ok = np.where(
        medium_hazard > P,
        score_max,
        np.where(high_hazard > P, risk_credit_medium, score_min),
    )
    trust_credit_lower = _var_float(
        "CONFIG_TRUST_CREDIT_LOWER", (score_min + score_max) / 2
    )
    trust_ok = np.where(trust_full_credit <= T, score_max, trust_credit_lower)
    score = (
        w_budget * score_max * np.ones_like(T)
        + w_risk * risk_ok
        + w_trust * trust_ok
        + w_completeness * score_max
    )
    score = np.where(trust_hard_floor > T, score_min, score)

    cmap = ListedColormap(["#7F1D1D", "#F4B44A", "#0A7A43"], name="gate_decision")
    norm = BoundaryNorm(
        [score_min, hold_threshold, execute_threshold, score_max + 0.001], cmap.N
    )

    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    ax.set_facecolor("#080808")
    fig.patch.set_facecolor("#F7F9FC")

    im = ax.pcolormesh(
        trust_vals, pressure_vals, score, cmap=cmap, norm=norm, shading="auto"
    )

    cbar_ticks = [
        (score_min + hold_threshold) / 2,
        (hold_threshold + execute_threshold) / 2,
        (execute_threshold + score_max) / 2,
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

    ax.axvspan(score_min, trust_hard_floor, alpha=0.62, color="#000000", zorder=2)
    ax.text(
        trust_hard_floor / 2,
        pressure_max * 0.92,
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
        score_max * 0.88,
        pressure_max * 0.12,
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
        score_max * 0.48,
        pressure_max * 0.58,
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
        score_max * 0.18,
        pressure_max * 0.83,
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
            pressure_max * 0.972,
            f"{x_val} {label_txt.replace(chr(10), ' ')}",
            fontsize=7.2,
            color="white",
            ha="left",
            alpha=0.82,
            zorder=3,
            va="top",
        )

    for y_val, label_txt in [
        (medium_hazard, "medium hazard"),
        (high_hazard, "high hazard"),
    ]:
        ax.axhline(y=y_val, color="white", lw=0.8, alpha=0.32, linestyle=":")
        ax.text(
            score_max * 0.985,
            y_val + pressure_max * 0.008,
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
            return score_min
        risk_component = (
            score_max
            if risk_pressure < medium_hazard
            else risk_credit_medium
            if risk_pressure < high_hazard
            else score_min
        )
        trust_component = (
            score_max if trust_score >= trust_full_credit else trust_credit_lower
        )
        return (
            w_budget * score_max
            + w_risk * risk_component
            + w_trust * trust_component
            + w_completeness * score_max
        )

    def _decision(score_value: float) -> str:
        if score_value >= execute_threshold:
            return "EXECUTE"
        if score_value >= hold_threshold:
            return "HOLD"
        return "REFUSE"

    examples = [
        (
            min(score_max, max(trust_full_credit, score_max * 0.9)),
            medium_hazard / 2,
            score_max * 0.73,
            pressure_max * 0.17,
            "high trust\nclear field",
            "white",
        ),
        (
            min(score_max, max(trust_full_credit, score_max * 0.7)),
            high_hazard + (pressure_max - high_hazard) / 2,
            score_max * 0.78,
            pressure_max * 0.73,
            "elevated\nhazard",
            "#FFE066",
        ),
        (
            trust_hard_floor / 2,
            medium_hazard / 2,
            score_max * 0.33,
            pressure_max * 0.19,
            "low trust\nclear field",
            "#FF9999",
        ),
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
    ax.set_ylabel("Effective hazard = max(RISK, FAILURE)", fontsize=11.5)
    gate_title = (
        "Gate decision landscape — piecewise score bands and hard trust floor\n"
        f"score = {w_budget:.2f}*budget + {w_risk:.2f}*risk_ok + "
        f"{w_trust:.2f}*trust_ok + {w_completeness:.2f}*completeness\n"
        f"(budget={score_max:.1f}, completeness={score_max:.1f}; "
        f"trust_ok tiers at {trust_full_credit:.2f}; "
        f"trust < {trust_hard_floor:.2f} forces score={score_min:.1f})\n"
        f"{_var_str('CONFIG_PARAMETER_STATUS_SHORT', 'Current default/illustrative policy slice')}"
    )
    ax.set_title(gate_title, fontsize=9.5, pad=10)
    ax.tick_params(labelsize=9.5)
    _add_provenance_note(fig, color="#6B7280")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    _save(fig, "gate_score_heatmap.png")
