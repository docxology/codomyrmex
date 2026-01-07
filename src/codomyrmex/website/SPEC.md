# Website Module Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview
The Website module provides a flexible, template-based system for generating documentation and operational dashboards for the Codomyrmex project.

## Architecture

### Components
1.  **Generator** (`generator.py`): Core logic that renders templates with provided data.
2.  **Data Provider** (`data_provider.py`): Abstraction layer to fetch and normalize data from other Codomyrmex modules.
3.  **Templates** (`templates/`): Jinja2 templates for the HTML structure.
4.  **Assets** (`assets/`): Static files (CSS, JS, images).

### Data Flow
1.  Generator instantiates DataProvider.
2.  DataProvider queries system state (file system, databases, other module APIs).
3.  Generator loads Jinja2 templates.
4.  Generator renders templates with data.
5.  Generator writes static HTML files to the output directory.
6.  Generator copies static assets to the output directory.

## Interfaces

### WebsiteGenerator
```python
class WebsiteGenerator:
    def __init__(self, output_dir: str): ...
    def generate(self) -> None: ...
```

### DataProvider
```python
class DataProvider:
    def get_system_summary(self) -> dict: ...
    def get_agents_status(self) -> list[dict]: ...
    # ... other data methods
```

## Dependencies
- **Jinja2**: For template rendering.
- **Standard Library**: `pathlib`, `json`, `shutil`.
