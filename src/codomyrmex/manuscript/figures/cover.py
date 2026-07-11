"""Manuscript figure: cover art."""

from __future__ import annotations

from codomyrmex.manuscript.figures._common import (
    _COVER,
    RegularPolygon,
    _bezier,
    _figure_provenance,
    _glow,
    _save,
    _var_str,
    math,
    np,
    plt,
)


def fig_cover_art() -> None:
    BG = _COVER["bg"]
    W, H = 12.0, 6.5
    CX, CY = 0.0, 0.0

    fig = plt.figure(figsize=(W, H))
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_facecolor(BG)
    ax.set_xlim(-W / 2, W / 2)
    ax.set_ylim(-H / 2, H / 2)
    ax.set_aspect("equal")
    ax.axis("off")

    subsystems = [
        ("PheromoneStore", _COVER["phero"], "Pheromone\nStore"),
        ("ResourceLedger", _COVER["ledger"], "Resource\nLedger"),
        ("ActuationGate", _COVER["gate"], "Actuation\nGate"),
        ("ConsequenceMemory", _COVER["memory"], "Consequence\nMemory"),
        ("RoleAdapter", _COVER["role"], "Role\nAdapter"),
        ("PruningDaemon", _COVER["prune"], "Pruning\nDaemon"),
        ("FalsificationWorker", _COVER["falsif"], "Falsification\nWorker"),
    ]
    n_sub = len(subsystems)
    R_sub = 2.2
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
                ax.add_patch(
                    RegularPolygon(
                        (hx, hy),
                        numVertices=6,
                        radius=0.28,
                        orientation=0,
                        fill=False,
                        edgecolor=_COVER["grid"],
                        linewidth=0.30,
                        alpha=0.50,
                        zorder=0,
                    )
                )

    # Background radial glow
    for k in range(24, 0, -1):
        r = 0.12 + k * 0.19
        ax.add_patch(
            plt.Circle(
                (CX, CY),
                r,
                color=_COVER["kernel"],
                alpha=0.018 * (1 - k / 26),
                zorder=0,
            )
        )

    # Orbital ring
    theta = np.linspace(0, 2 * math.pi, 300)
    ax.plot(
        R_sub * np.cos(theta),
        R_sub * np.sin(theta),
        color="#1A2E42",
        lw=0.55,
        alpha=0.55,
        zorder=1,
    )

    # Ghostly spokes
    for i, (_, color, _) in enumerate(subsystems):
        ax.plot(
            [CX, sx[i]],
            [CY, sy[i]],
            color=color,
            alpha=0.09,
            lw=0.55,
            zorder=1,
            linestyle="--",
        )

    # Pheromone trails + particles
    n_particles = 11
    for i, (_, color, _) in enumerate(subsystems):
        bx, by = _bezier((sx[i], sy[i]), (CX, CY), curvature=0.38, n_pts=150)
        for seg in range(0, len(bx) - 4, 4):
            frac = seg / len(bx)
            ax.plot(
                bx[seg : seg + 5],
                by[seg : seg + 5],
                color=color,
                alpha=0.08 + frac * 0.28,
                lw=0.85,
                zorder=2,
            )
        bx2, by2 = _bezier((CX, CY), (sx[i], sy[i]), curvature=-0.20, n_pts=150)
        ax.plot(bx2, by2, color=color, alpha=0.09, lw=0.40, zorder=2, linestyle=":")
        for j in range(n_particles):
            frac = 0.05 + j * (0.90 / (n_particles - 1))
            idx = int(frac * (len(bx) - 1))
            ax.scatter(
                bx[idx],
                by[idx],
                color=color,
                s=5 + j * 9,
                alpha=0.65 + j * 0.03,
                zorder=4,
                linewidths=0,
            )

    # Outer agent ring (18 agents)
    n_agents = 18
    for k in range(n_agents):
        ag_a = 2 * math.pi * k / n_agents
        ax_pos = R_outer * math.cos(ag_a)
        ay_pos = R_outer * math.sin(ag_a)
        dists = [
            math.sqrt((ax_pos - sx[j]) ** 2 + (ay_pos - sy[j]) ** 2)
            for j in range(n_sub)
        ]
        nearest = int(np.argmin(dists))
        ag_color = subsystems[nearest][1]
        ax.plot(
            [ax_pos, sx[nearest]],
            [ay_pos, sy[nearest]],
            color=ag_color,
            alpha=0.07,
            lw=0.28,
            zorder=1,
        )
        _glow(
            ax,
            ax_pos,
            ay_pos,
            ag_color,
            r_core=0.038,
            r_max=0.13,
            n_rings=6,
            alpha_peak=0.22,
            zorder=3,
        )

    # Subsystem nodes
    for i, (_, color, short) in enumerate(subsystems):
        _glow(
            ax,
            sx[i],
            sy[i],
            color,
            r_core=0.23,
            r_max=0.68,
            n_rings=13,
            alpha_peak=0.17,
            zorder=5,
        )
        lx = R_label * math.cos(angles[i])
        ly = R_label * math.sin(angles[i])
        if i == 0:
            lx = sx[i]
            ly = sy[i] - 0.72
        ax.text(
            lx,
            ly,
            short,
            fontsize=6.5,
            color=color,
            ha="center",
            va="center",
            fontweight="bold",
            zorder=7,
            linespacing=1.4,
        )

    # ColonyKernel hub
    _glow(
        ax,
        CX,
        CY,
        _COVER["kernel"],
        r_core=0.34,
        r_max=0.98,
        n_rings=16,
        alpha_peak=0.21,
        zorder=6,
    )
    ax.text(
        CX,
        CY + 0.11,
        "Colony",
        fontsize=11,
        color="white",
        ha="center",
        va="center",
        fontweight="bold",
        zorder=9,
        fontfamily="monospace",
    )
    ax.text(
        CX,
        CY - 0.21,
        "Kernel",
        fontsize=11,
        color="white",
        ha="center",
        va="center",
        fontweight="bold",
        zorder=9,
        fontfamily="monospace",
    )

    # Title
    subtitle = _var_str(
        "CONFIG_SUBTITLE",
        "Colony Control Plane, Stigmergic Pressure, and Falsification-Gated Actuation",
    )
    ax.text(
        0,
        H / 2 - 0.24,
        "C O D O M Y R M E X",
        fontsize=22,
        color=_COVER["text"],
        ha="center",
        va="top",
        fontweight="bold",
        zorder=10,
        fontfamily="monospace",
    )
    ax.plot(
        [-2.6, 2.6],
        [H / 2 - 0.62, H / 2 - 0.62],
        color=_COVER["dim"],
        lw=0.75,
        alpha=0.50,
        zorder=10,
    )
    ax.text(
        0,
        H / 2 - 0.79,
        subtitle,
        fontsize=9,
        color=_COVER["dim"],
        ha="center",
        va="top",
        zorder=10,
        style="italic",
    )
    ax.text(
        -W / 2 + 0.14,
        -H / 2 + 0.14,
        "Colony Control Plane  ·  Stigmergic Pressure  ·  Falsification-Gated Actuation",
        fontsize=6,
        color=_COVER["dim"],
        ha="left",
        va="bottom",
        zorder=10,
    )
    ax.text(
        W / 2 - 0.14,
        -H / 2 + 0.14,
        _figure_provenance(),
        fontsize=5.8,
        color=_COVER["dim"],
        ha="right",
        va="bottom",
        zorder=10,
    )

    _save(fig, "cover.png")
