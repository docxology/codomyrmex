# data/

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Data layer for test_project providing input data storage and processed output directories.

## Directory Structure

```
data/
├── input/              # Source data for analysis
│   └── sample_data.json
├── processed/          # Processed analysis outputs
├── README.md
├── AGENTS.md
├── SPEC.md
└── PAI.md
```

## Input Data

The `input/` directory contains sample data files:

- **sample_data.json**: Example project analysis data for testing and demonstration

## Processed Data

The `processed/` directory stores intermediate results from pipeline execution:

- Analysis results
- Cached computations
- Intermediate processing outputs

## Usage

```python
from pathlib import Path
import json

# Load sample data
data_dir = Path("data/input")
with open(data_dir / "sample_data.json") as f:
    sample = json.load(f)
    
print(f"Files: {len(sample['files'])}")
```

## Navigation

- **Parent**: [../README.md](../README.md)
- **Sibling**: [../config/](../config/), [../src/](../src/), [../reports/](../reports/)
