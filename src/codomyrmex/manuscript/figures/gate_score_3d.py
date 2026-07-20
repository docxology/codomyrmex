"""Manuscript figure: gate score 3d."""

from __future__ import annotations

from codomyrmex.manuscript.figures._common import (
    _OI,
    _add_provenance_note,
    _pub_style,
    _save,
    _var_float,
    np,
    plt,
)


def fig_gate_score_3d() -> None:
    """3D surface with budget and local-hazard clearance fixed at 1.0.

    The trust hard floor and tiered trust credit mirror ActuationGate. Completeness
    is continuous only as a visual envelope; runtime values are discrete.
    """
    from mpl_toolkits.mplot3d import Axes3D

    w_trust = _var_float("CONFIG_GATE_WEIGHT_TRUST", 0.25)
    w_complete = _var_float("CONFIG_GATE_WEIGHT_COMPLETENESS", 0.15)
    gate_exec = _var_float("CONFIG_GATE_EXECUTE_THRESHOLD", 0.75)
    gate_hold = _var_float("CONFIG_GATE_HOLD_THRESHOLD", 0.50)
    trust_floor = _var_float("CONFIG_TRUST_HARD_FLOOR", 0.30)

    trust = np.linspace(0, 1, 60)
    completeness = np.linspace(0, 1, 60)
    T, C = np.meshgrid(trust, completeness)

    trust_credit = np.where(T >= 0.60, 1.0, 0.5)
    score_best = 0.60 + w_trust * trust_credit + w_complete * C
    score_best = np.where(trust_floor > T, 0.0, score_best)

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
    ax1.set_title(
        "3D gate score surface\n(budget=hazard clearance=1.0)",
        fontsize=10,
        pad=8,
    )

    # ── Right panel: same data as 2D heatmap slices ──
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.set_facecolor("#F7F9FC")
    _pub_style(ax2)

    for trust_val, ls, marker, color in [
        (0.2, "--", "v", "#D55E00"),
        (0.5, "-.", "s", _OI["blue"]),
        (0.9, "-", "o", _OI["green"]),
    ]:
        if trust_val < trust_floor:
            total_score = np.zeros_like(C[:, 0])
        else:
            trust_component = 1.0 if trust_val >= 0.60 else 0.5
            total_score = 0.60 + w_trust * trust_component + w_complete * C[:, 0]
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
    ax2.fill_between(C[:, 0], 0.0, gate_hold, alpha=0.06, color="#D55E00")
    ax2.fill_between(C[:, 0], gate_hold, gate_exec, alpha=0.06, color=_OI["yellow"])
    ax2.fill_between(C[:, 0], gate_exec, 1.0, alpha=0.06, color=_OI["green"])

    ax2.set_xlabel("Completeness score", fontsize=9)
    ax2.set_ylabel("Gate score g", fontsize=9)
    ax2.set_title(
        "Score slices at fixed trust levels\n(budget=hazard clearance=1.0)",
        fontsize=10,
    )
    ax2.legend(fontsize=7.5, loc="lower right", framealpha=0.85)
    ax2.set_ylim(-0.02, 1.05)

    _add_provenance_note(fig)
    fig.tight_layout(pad=0.6, rect=(0, 0.035, 1, 1))
    _save(fig, "gate_score_3d.png")
