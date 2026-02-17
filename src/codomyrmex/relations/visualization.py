from .crm import ContactManager
from codomyrmex.data_visualization.plots.mermaid import MermaidDiagram


def render_social_graph(cm: ContactManager) -> MermaidDiagram:
    """
    Generates a mermaid diagram of social connections.
    """
    diagram = "graph TD\n"

    # Simple flat graph for now as we don't have explicit edges in the basic CRM
    for contact in cm._contacts.values():
        safe_name = contact.name.replace(" ", "_")
        diagram += f"    {safe_name}[{contact.name}]\n"

    return MermaidDiagram(title="Social Graph", definition=diagram)
