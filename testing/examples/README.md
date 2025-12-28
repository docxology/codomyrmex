# testing/examples

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

This directory contains examples demonstrating testing capabilities and validation workflows in the Codomyrmex platform. These examples show how to run tests, validate configurations, and execute example workflows.

## Directory Structure

```
testing/examples/
├── README.md                 # This file
├── AGENTS.md                 # Agent coordination document
├── conftest.py               # Pytest configuration for examples
├── reports/                  # Generated test reports
├── config_validation.py      # Configuration validation examples
├── example_execution.py      # Example execution patterns
└── output_validation.py      # Output validation workflows
```

## Quick Start

### Running Example Tests

```bash
# From testing/examples directory
pytest config_validation.py -v
pytest example_execution.py -v
pytest output_validation.py -v
```

### Running All Examples

```bash
# From testing directory
pytest examples/ -v --tb=short
```