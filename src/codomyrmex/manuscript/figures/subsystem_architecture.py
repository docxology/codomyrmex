"""Manuscript figure: subsystem architecture."""

from __future__ import annotations

from codomyrmex.manuscript.figures._common import (
    _OI,
    RegularPolygon,
    _add_provenance_note,
    _save,
    _var_str,
    math,
    np,
    plt,
)


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
