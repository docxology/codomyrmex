"""Replay the native dependency ordering on a fictional publishing graph."""

import argparse
import json
import shutil
import sys
from pathlib import Path

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "project", type=Path, help="New disposable Template project directory"
    )
    project = parser.parse_args().project.resolve()
    if project.exists() or project.is_relative_to(REPO):
        parser.error("Choose a new project directory outside the source checkout.")

    # The sparse checkout provides only the reviewed graph utility.
    sys.path.insert(0, str(REPO / "src"))
    from codomyrmex.utils.graph import kahn_topological_sort

    dependencies = {
        "Draft": (),
        "Copyedit": ("Draft",),
        "Illustrate": ("Draft",),
        "Assemble": ("Copyedit", "Illustrate"),
    }
    order = kahn_topological_sort(dependencies, dependencies.__getitem__)
    if set(order) != set(dependencies) or len(order) != len(dependencies):
        raise ValueError("The order does not contain each task exactly once.")
    position = {task: index for index, task in enumerate(order)}
    if any(
        position[prior] >= position[task]
        for task, prerequisites in dependencies.items()
        for prior in prerequisites
    ):
        raise ValueError("A prerequisite occurs after its dependent task.")

    cycle = {"Copyedit": ("Assemble",), "Assemble": ("Copyedit",)}
    try:
        kahn_topological_sort(cycle, cycle.__getitem__)
    except ValueError:
        cycle_rejected = True
    else:
        raise ValueError("The two-task cycle should have raised ValueError.")

    figures = project / "output" / "figures"
    data = project / "output" / "data"
    figures.mkdir(parents=True, exist_ok=True)
    data.mkdir(parents=True, exist_ok=True)
    evidence = {
        "prerequisites": dependencies,
        "order": order,
        "cycle_rejected": cycle_rejected,
    }
    (data / "graph_fixture.json").write_text(
        json.dumps(evidence, indent=2) + "\n", encoding="utf-8"
    )

    figure = Figure(figsize=(6.0, 2.0), layout="constrained")
    FigureCanvasAgg(figure)
    axes = figure.subplots()
    axes.scatter(range(len(order)), [0] * len(order), color="#216282", zorder=2)
    axes.axhline(0, color="#697984", zorder=1)
    axes.set(
        xticks=list(range(len(order))),
        xticklabels=order,
        yticks=[],
        ylim=(-0.15, 0.15),
        xlabel="Order returned by the repository utility",
    )
    filename = "publishing_order.png"
    figure.savefig(figures / filename, dpi=160)
    if (figures / filename).read_bytes() != (HERE / filename).read_bytes():
        raise ValueError(
            "The generated figure differs from the retained reference PNG."
        )

    manuscript = project / "docs" / "manuscript"
    manuscript.mkdir(parents=True)
    for source in sorted((REPO / "tests" / "unit" / "utils").glob("reader-*.in")):
        shutil.copyfile(
            source, manuscript / source.name.removeprefix("reader-").removesuffix(".in")
        )
    registry = {
        "fig:publishing-order": {
            "filename": filename,
            "caption": "One valid ordering of a fictional publishing checklist.",
            "alt_text": "From left to right: draft, copyedit, illustrate, assemble.",
        }
    }
    (figures / "figure_registry.json").write_text(
        json.dumps(registry, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
