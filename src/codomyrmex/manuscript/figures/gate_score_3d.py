"""Manuscript figure: gate score 3d."""

from __future__ import annotations

from codomyrmex.manuscript.figures._common import (
    _OI,
    _add_provenance_note,
    _experiment_float,
    _figure_parameter,
    _figure_parameter_list,
    _pub_style,
    _save,
    _var_float,
    _var_str,
    np,
    plt,
)


def fig_gate_score_3d() -> None:
    """3D surface with budget and local-hazard clearance fixed at 1.0.

    The trust hard floor and tiered trust credit mirror ActuationGate. Completeness
    is continuous only as a visual envelope; runtime values are discrete.
    """
    from mpl_toolkits.mplot3d import Axes3D

    score_min = float(_figure_parameter("score_min", "CONFIG_SCORE_MIN", 0.0))
    score_max = float(_figure_parameter("score_max", "CONFIG_SCORE_MAX", 1.0))
    grid_points = int(
        _figure_parameter(
            "gate_surface_grid_points", "CONFIG_GATE_SURFACE_GRID_POINTS", 60, int
        )
    )
    w_budget = _var_float("CONFIG_GATE_WEIGHT_BUDGET", 0.30)
    w_risk = _var_float("CONFIG_GATE_WEIGHT_RISK", 0.30)
    w_trust = _var_float("CONFIG_GATE_WEIGHT_TRUST", 0.25)
    w_complete = _var_float("CONFIG_GATE_WEIGHT_COMPLETENESS", 0.15)
    gate_exec = _var_float("CONFIG_GATE_EXECUTE_THRESHOLD", 0.75)
    gate_hold = _var_float("CONFIG_GATE_HOLD_THRESHOLD", 0.50)
    trust_floor = _var_float("CONFIG_TRUST_HARD_FLOOR", 0.30)
    trust_full_credit = _var_float("CONFIG_TRUST_FULL_CREDIT_THRESHOLD", 0.60)

    trust = np.linspace(score_min, score_max, grid_points)
    completeness = np.linspace(score_min, score_max, grid_points)
    T, C = np.meshgrid(trust, completeness)

    trust_credit_lower = _var_float(
        "CONFIG_TRUST_CREDIT_LOWER", (score_min + score_max) / 2
    )
    trust_credit = np.where(trust_full_credit <= T, score_max, trust_credit_lower)
    score_base = w_budget * score_max + w_risk * score_max
    score_best = score_base + w_trust * trust_credit + w_complete * C
    score_best = np.where(trust_floor > T, score_min, score_best)

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

    norm = plt.Normalize(score_min, score_max)
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
    ax1.set_title(
        f"3D gate score surface\n(budget=hazard clearance={score_max:.1f})",
        fontsize=10,
        pad=8,
    )

    # ── Right panel: same data as 2D heatmap slices ──
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.set_facecolor("#F7F9FC")
    _pub_style(ax2)

    trust_slice_values = _figure_parameter_list(
        "gate_surface_trust_slices", "CONFIG_GATE_SURFACE_TRUST_SLICES"
    )
    slice_styles = [
        ("--", "v", "#D55E00"),
        ("-.", "s", _OI["blue"]),
        ("-", "o", _OI["green"]),
    ]
    for trust_val, (ls, marker, color) in zip(
        trust_slice_values, slice_styles, strict=False
    ):
        if trust_val < trust_floor:
            total_score = np.full_like(C[:, 0], score_min)
        else:
            trust_component = (
                score_max if trust_val >= trust_full_credit else trust_credit_lower
            )
            total_score = score_base + w_trust * trust_component + w_complete * C[:, 0]
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
    ax2.fill_between(C[:, 0], score_min, gate_hold, alpha=0.06, color="#D55E00")
    ax2.fill_between(C[:, 0], gate_hold, gate_exec, alpha=0.06, color=_OI["yellow"])
    ax2.fill_between(C[:, 0], gate_exec, score_max, alpha=0.06, color=_OI["green"])

    ax2.set_xlabel("Completeness score", fontsize=9)
    ax2.set_ylabel("Gate score g", fontsize=9)
    ax2.set_title(
        f"Score slices at fixed trust levels\n"
        f"(budget=hazard clearance={score_max:.1f})\n"
        f"{_var_str('CONFIG_PARAMETER_STATUS_SHORT', 'Current default/illustrative policy slice')}",
        fontsize=10,
    )
    ax2.legend(fontsize=7.5, loc="lower right", framealpha=0.85)
    ax2.set_ylim(score_min - 0.02, score_max + 0.05)

    _add_provenance_note(fig)
    fig.tight_layout(pad=0.6, rect=(0, 0.035, 1, 1))
    _save(fig, "gate_score_3d.png")
