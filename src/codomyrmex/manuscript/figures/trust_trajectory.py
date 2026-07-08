"""Manuscript figure: trust trajectory."""

from __future__ import annotations

from codomyrmex.manuscript.figures._common import (
    _OI,
    _add_provenance_note,
    _experiment_float,
    _pub_style,
    _role_min_proposals,
    _role_threshold,
    _save,
    _var_float,
    math,
    mpatches,
    plt,
    ticker,
)


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
