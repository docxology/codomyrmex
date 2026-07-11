"""Manuscript figure: colony pressure loop."""

from __future__ import annotations

from codomyrmex.manuscript.figures._common import (
    _OI,
    FancyBboxPatch,
    _add_provenance_note,
    _save,
    math,
    np,
    plt,
)


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
