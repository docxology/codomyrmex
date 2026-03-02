"""
Mermaid diagram generation utilities.

Provides utilities for creating Mermaid diagrams programmatically.
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class DiagramType(Enum):
    """Types of Mermaid diagrams."""
    FLOWCHART = "flowchart"
    SEQUENCE = "sequenceDiagram"
    CLASS = "classDiagram"
    STATE = "stateDiagram-v2"
    ER = "erDiagram"
    GANTT = "gantt"
    PIE = "pie"
    MINDMAP = "mindmap"
    TIMELINE = "timeline"
    JOURNEY = "journey"


class FlowDirection(Enum):
    """Direction for flowcharts."""
    TOP_DOWN = "TD"
    TOP_BOTTOM = "TB"
    BOTTOM_TOP = "BT"
    LEFT_RIGHT = "LR"
    RIGHT_LEFT = "RL"


class NodeShape(Enum):
    """Flowchart node shapes."""
    RECTANGLE = "rect"
    ROUND = "round"
    STADIUM = "stadium"
    SUBROUTINE = "subroutine"
    CYLINDER = "cylinder"
    CIRCLE = "circle"
    ASYMMETRIC = "asymmetric"
    RHOMBUS = "rhombus"
    HEXAGON = "hexagon"
    PARALLELOGRAM = "parallelogram"
    TRAPEZOID = "trapezoid"


@dataclass
class Node:
    """A node in a flowchart."""
    id: str
    label: str
    shape: NodeShape = NodeShape.RECTANGLE
    style: str | None = None

    def render(self) -> str:
        """Render the node definition."""
        label = self.label.replace('"', "'")

        shape_formats = {
            NodeShape.RECTANGLE: f'{self.id}["{label}"]',
            NodeShape.ROUND: f'{self.id}("{label}")',
            NodeShape.STADIUM: f'{self.id}(["{label}"])',
            NodeShape.SUBROUTINE: f'{self.id}[["{label}"]]',
            NodeShape.CYLINDER: f'{self.id}[(("{label}"))]',
            NodeShape.CIRCLE: f'{self.id}((("{label}")))',
            NodeShape.ASYMMETRIC: f'{self.id}>"{label}"]',
            NodeShape.RHOMBUS: f'{self.id}{{"{label}"}}',
            NodeShape.HEXAGON: f'{self.id}{{{{"{label}"}}}}',
            NodeShape.PARALLELOGRAM: f'{self.id}[/"{label}"/]',
            NodeShape.TRAPEZOID: f'{self.id}[/"{label}"\\]',
        }

        return shape_formats.get(self.shape, f'{self.id}["{label}"]')


class LinkStyle(Enum):
    """Styles for links between nodes."""
    SOLID = "-->"
    DOTTED = "-.->"
    THICK = "==>"
    INVISIBLE = "~~~"


@dataclass
class Link:
    """A link between nodes in a flowchart."""
    source: str
    target: str
    label: str | None = None
    style: LinkStyle = LinkStyle.SOLID

    def render(self) -> str:
        """Render the link."""
        if self.label:
            label = self.label.replace('"', "'")
            style_str = self.style.value.replace(">", f"|{label}|>")
            return f"{self.source} {style_str} {self.target}"
        return f"{self.source} {self.style.value} {self.target}"


class MermaidDiagram:
    """Base class for Mermaid diagrams."""

    def __init__(self, diagram_type: DiagramType):
        """Initialize this instance."""
        self.diagram_type = diagram_type
        self._content: list[str] = []
        self._config: dict[str, Any] = {}

    def add_directive(self, directive: str) -> 'MermaidDiagram':
        """Add a directive."""
        self._content.insert(0, f"%%{{{directive}}}%%")
        return self

    def set_config(self, config: dict[str, Any]) -> 'MermaidDiagram':
        """Set Mermaid configuration."""
        self._config = config
        return self

    def render(self) -> str:
        """Render the diagram to Mermaid syntax."""
        lines = []

        if self._config:
            lines.append("%%{init: " + json.dumps(self._config) + "}%%")

        lines.append(self.diagram_type.value)
        lines.extend(self._content)

        return "\n".join(lines)

    def to_markdown(self) -> str:
        """Render as a Markdown code block."""
        return f"```mermaid\n{self.render()}\n```"


class Flowchart(MermaidDiagram):
    """Flowchart diagram builder."""

    def __init__(self, direction: FlowDirection = FlowDirection.TOP_DOWN):
        """Initialize this instance."""
        super().__init__(DiagramType.FLOWCHART)
        self.direction = direction
        self._nodes: dict[str, Node] = {}
        self._links: list[Link] = []
        self._subgraphs: list[dict[str, Any]] = []

    def add_node(
        self,
        node_id: str,
        label: str,
        shape: NodeShape = NodeShape.RECTANGLE,
        style: str | None = None,
    ) -> 'Flowchart':
        """Add a node to the flowchart."""
        self._nodes[node_id] = Node(node_id, label, shape, style)
        return self

    def add_link(
        self,
        source: str,
        target: str,
        label: str | None = None,
        style: LinkStyle = LinkStyle.SOLID,
    ) -> 'Flowchart':
        """Add a link between nodes."""
        self._links.append(Link(source, target, label, style))
        return self

    def add_subgraph(
        self,
        subgraph_id: str,
        title: str,
        node_ids: list[str],
    ) -> 'Flowchart':
        """Add a subgraph containing nodes."""
        self._subgraphs.append({
            "id": subgraph_id,
            "title": title,
            "nodes": node_ids,
        })
        return self

    def render(self) -> str:
        """Render the flowchart."""
        lines = []

        if self._config:
            lines.append("%%{init: " + json.dumps(self._config) + "}%%")

        lines.append(f"flowchart {self.direction.value}")

        # Render nodes
        for node in self._nodes.values():
            lines.append(f"    {node.render()}")

        # Render subgraphs
        for subgraph in self._subgraphs:
            lines.append(f"    subgraph {subgraph['id']}[\"{subgraph['title']}\"]")
            for node_id in subgraph["nodes"]:
                if node_id in self._nodes:
                    lines.append(f"        {self._nodes[node_id].render()}")
            lines.append("    end")

        # Render links
        for link in self._links:
            lines.append(f"    {link.render()}")

        return "\n".join(lines)


class SequenceDiagram(MermaidDiagram):
    """Sequence diagram builder."""

    def __init__(self):
        """Initialize this instance."""
        super().__init__(DiagramType.SEQUENCE)
        self._participants: list[dict[str, str]] = []
        self._messages: list[str] = []

    def add_participant(
        self,
        alias: str,
        label: str | None = None,
        actor: bool = False,
    ) -> 'SequenceDiagram':
        """Add a participant."""
        participant_type = "actor" if actor else "participant"
        if label:
            self._participants.append({
                "type": participant_type,
                "alias": alias,
                "label": label,
            })
        else:
            self._participants.append({
                "type": participant_type,
                "alias": alias,
            })
        return self

    def add_message(
        self,
        sender: str,
        receiver: str,
        message: str,
        arrow_type: str = "->>"  # ->>, -->, ->>+, -x, etc.
    ) -> 'SequenceDiagram':
        """Add a message between participants."""
        self._messages.append(f"{sender}{arrow_type}{receiver}: {message}")
        return self

    def add_note(
        self,
        text: str,
        position: str = "right of",  # right of, left of, over
        participant: str = "",
    ) -> 'SequenceDiagram':
        """Add a note."""
        self._messages.append(f"Note {position} {participant}: {text}")
        return self

    def add_loop(
        self,
        label: str,
        messages: list[tuple],
    ) -> 'SequenceDiagram':
        """Add a loop block."""
        self._messages.append(f"loop {label}")
        for sender, receiver, message in messages:
            self._messages.append(f"    {sender}->>{receiver}: {message}")
        self._messages.append("end")
        return self

    def render(self) -> str:
        """Render the sequence diagram."""
        lines = []

        if self._config:
            lines.append("%%{init: " + json.dumps(self._config) + "}%%")

        lines.append("sequenceDiagram")

        for participant in self._participants:
            if "label" in participant:
                lines.append(f"    {participant['type']} {participant['alias']} as {participant['label']}")
            else:
                lines.append(f"    {participant['type']} {participant['alias']}")

        for message in self._messages:
            lines.append(f"    {message}")

        return "\n".join(lines)


class ClassDiagram(MermaidDiagram):
    """Class diagram builder."""

    def __init__(self):
        """Initialize this instance."""
        super().__init__(DiagramType.CLASS)
        self._classes: dict[str, dict[str, Any]] = {}
        self._relationships: list[str] = []

    def add_class(
        self,
        name: str,
        attributes: list[str] | None = None,
        methods: list[str] | None = None,
    ) -> 'ClassDiagram':
        """Add a class to the diagram."""
        self._classes[name] = {
            "attributes": attributes or [],
            "methods": methods or [],
        }
        return self

    def add_relationship(
        self,
        class1: str,
        class2: str,
        relationship: str = "-->",  # <|-- inheritance, *-- composition, o-- aggregation
        label: str | None = None,
    ) -> 'ClassDiagram':
        """Add a relationship between classes."""
        rel = f"{class1} {relationship} {class2}"
        if label:
            rel += f" : {label}"
        self._relationships.append(rel)
        return self

    def render(self) -> str:
        """Render the class diagram."""
        lines = [self.diagram_type.value]

        for class_name, data in self._classes.items():
            lines.append(f"    class {class_name} {{")
            for attr in data["attributes"]:
                lines.append(f"        {attr}")
            for method in data["methods"]:
                lines.append(f"        {method}")
            lines.append("    }")

        for rel in self._relationships:
            lines.append(f"    {rel}")

        return "\n".join(lines)


def create_flowchart(
    direction: FlowDirection = FlowDirection.TOP_DOWN
) -> Flowchart:
    """Create a new flowchart."""
    return Flowchart(direction)


def create_sequence_diagram() -> SequenceDiagram:
    """Create a new sequence diagram."""
    return SequenceDiagram()


def create_class_diagram() -> ClassDiagram:
    """Create a new class diagram."""
    return ClassDiagram()


__all__ = [
    "DiagramType",
    "FlowDirection",
    "NodeShape",
    "Node",
    "LinkStyle",
    "Link",
    "MermaidDiagram",
    "Flowchart",
    "SequenceDiagram",
    "ClassDiagram",
    "create_flowchart",
    "create_sequence_diagram",
    "create_class_diagram",
]
