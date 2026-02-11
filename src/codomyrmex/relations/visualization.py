from .crm import CRM
from codomyrmex.visualization import MermaidDiagram

def render_social_graph(crm: CRM) -> MermaidDiagram:
    """
    Generates a mermaid diagram of social connections.
    """
    diagram = "graph TD\n"
    
    # Simple flat graph for now as we don't have explicit edges in the basic CRM
    for contact in crm._contacts:
        safe_name = contact.name.replace(" ", "_")
        diagram += f"    {safe_name}[{contact.name}]\n"
        
    return MermaidDiagram("Social Graph", diagram)
