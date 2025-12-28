# Codomyrmex Agents — examples/documentation/examples

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

This is the agent coordination document for documentation generation examples. It defines the workflows that demonstrate Codomyrmex documentation capabilities.

## Function Signatures

### Basic Documentation Generation (`example_basic.py`)

```python
def generate_api_docs(source_path: str, output_path: str, config: dict) -> dict
```
Generates API documentation from source code.

```python
def create_module_guide(module_name: str, config: dict) -> str
```
Creates a usage guide for a specific module.

```python
def generate_integration_docs(services: list, output_format: str) -> dict
```
Generates integration documentation for multiple services.

### Configuration Handling

```python
def load_doc_config(config_path: str) -> dict
```
Loads documentation configuration from file.

```python
def validate_doc_config(config: dict) -> bool
```
Validates documentation configuration parameters.

```python
def merge_doc_configs(base_config: dict, override_config: dict) -> dict
```
Merges base and override documentation configurations.