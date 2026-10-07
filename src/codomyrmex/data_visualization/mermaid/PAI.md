# Mermaid - PAI

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Path

`codomyrmex.data_visualization.mermaid`

## Quick Use

```python
from codomyrmex.data_visualization.mermaid import FlowDirection, Flowchart

chart = Flowchart(direction=FlowDirection.LEFT_RIGHT)
chart.add_node("a", "Plan").add_node("b", "Build").add_link("a", "b")
print(chart.render())
```
