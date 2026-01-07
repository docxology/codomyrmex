# Website Generation Module

**Package**: `src.codomyrmex.website`
**Layer**: Service Layer

## Purpose
This module is responsible for generating static websites and dashboards to visualize the status, metrics, and operations of the Codomyrmex ecosystem. It serves as a central hub for human interaction with the system's data.

## Key Features
- **Static Site Generation**: Generates a self-contained HTML/CSS/JS website.
- **Dashboard**: Visualizes agent status, system metrics, and workflow states.
- **Data Integration**: Aggregates data from various system modules (agents, queue, build, etc.).
- **Zero-Dependency Viewing**: The output is standard HTML that can be viewed in any browser.

## Usage
The primary way to use this module is through the orchestrator script:

```bash
python scripts/website/generate.py --output-dir ./output/dashboard/
```

Programmatic usage:
```python
from codomyrmex.website.generator import WebsiteGenerator

generator = WebsiteGenerator(output_dir="./output/dashboard")
generator.generate()
```
