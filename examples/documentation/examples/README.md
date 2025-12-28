# examples/documentation/examples

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

This directory contains examples demonstrating documentation generation capabilities in the Codomyrmex platform. These examples show how to generate API documentation, create technical guides, and automate documentation workflows.

## Directory Structure

```
examples/documentation/examples/
├── README.md                 # This file
├── AGENTS.md                 # Agent coordination document
├── config.json               # Configuration examples
├── config.yaml               # YAML configuration
└── example_basic.py          # Basic documentation generation
```

## Quick Start

### Running Documentation Examples

```bash
# From examples/documentation/examples directory
python example_basic.py
```

### Configuration Options

```yaml
# config.yaml
output_format: "markdown"
source_paths:
  - "src/codomyrmex/"
include_private: false
generate_index: true
```

## Example Output

The examples generate documentation in various formats:
- API reference documentation
- Module usage guides
- Integration examples
- Technical specifications