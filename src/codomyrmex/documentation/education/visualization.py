from codomyrmex.data_visualization.plots.mermaid import MermaidDiagram

from .curriculum import Curriculum


def render_curriculum_path(curriculum: Curriculum) -> MermaidDiagram:
    """
    Generates a flowchart of the lesson dependencies.
    """
    diagram = "graph LR\n"

    for lesson in curriculum.lessons:
        safe_title = lesson.title.replace(" ", "_")
        diagram += f"    {lesson.id}[{lesson.title}]\n"

        for prereq_id in lesson.prerequisites:
            diagram += f"    {prereq_id} --> {lesson.id}\n"

    return MermaidDiagram(title="Curriculum Path", definition=diagram)
