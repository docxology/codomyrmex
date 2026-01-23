#!/usr/bin/env python3
"""
Batch generate RASP documentation for submodules.
"""

import os
from pathlib import Path

BASE = Path("/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex")

# Define all submodules that need RASP docs
SUBMODULES = {
    # collaboration
    "collaboration/agents": ("agents", "Multi-agent coordination", "Agent definitions and lifecycle management"),
    "collaboration/communication": ("communication", "Inter-agent messaging", "Message passing and channel management"),
    "collaboration/coordination": ("coordination", "Task coordination", "Task distribution and consensus protocols"),
    "collaboration/protocols": ("protocols", "Swarm protocols", "Swarm behavior and collaboration protocols"),
    
    # model_context_protocol
    "model_context_protocol/schemas": ("schemas", "MCP schemas", "Model context protocol schema definitions"),
    "model_context_protocol/adapters": ("adapters", "MCP adapters", "Integration adapters for AI providers"),
    "model_context_protocol/validators": ("validators", "Schema validators", "Schema validation utilities"),
    "model_context_protocol/discovery": ("discovery", "Service discovery", "MCP service discovery mechanisms"),
    
    # telemetry
    "telemetry/exporters": ("exporters", "Telemetry exporters", "OTLP and other telemetry exporters"),
    "telemetry/spans": ("spans", "Span processing", "Trace span processing and management"),
    "telemetry/context": ("context", "Trace context", "Trace context propagation"),
    "telemetry/metrics": ("metrics", "Metrics collection", "Metrics collectors and aggregators"),
    
    # feature_flags
    "feature_flags/core": ("core", "Core flag management", "Core feature flag manager"),
    "feature_flags/strategies": ("strategies", "Evaluation strategies", "Flag evaluation strategies"),
    "feature_flags/storage": ("storage", "Flag storage", "Backend storage for flags"),
    "feature_flags/evaluation": ("evaluation", "Flag evaluation", "Flag evaluation engine"),
    "feature_flags/rollout": ("rollout", "Gradual rollout", "Gradual rollout controls"),
    
    # embodiment
    "embodiment/ros": ("ros", "ROS integration", "ROS bridge and communication"),
    "embodiment/sensors": ("sensors", "Sensor interfaces", "Camera, lidar, IMU interfaces"),
    "embodiment/actuators": ("actuators", "Actuator control", "Motor, servo, gripper control"),
    "embodiment/transformation": ("transformation", "Transformations", "Coordinate transformations"),
    
    # evolutionary_ai
    "evolutionary_ai/population": ("population", "Population management", "Population lifecycle"),
    "evolutionary_ai/operators": ("operators", "Genetic operators", "Crossover and mutation"),
    "evolutionary_ai/genome": ("genome", "Genome representation", "Genome encoding"),
    "evolutionary_ai/selection": ("selection", "Selection methods", "Tournament, roulette selection"),
    "evolutionary_ai/fitness": ("fitness", "Fitness evaluation", "Fitness functions and evaluators"),
    
    # templating
    "templating/engines": ("engines", "Template engines", "Core template engine"),
    "templating/loaders": ("loaders", "Template loaders", "Template loading and management"),
    "templating/filters": ("filters", "Template filters", "Formatters and transforms"),
    "templating/context": ("context", "Context builders", "Template context construction"),
    
    # tree_sitter
    "tree_sitter/languages": ("languages", "Language support", "Language definitions"),
    "tree_sitter/parsers": ("parsers", "Code parsers", "Syntax parsing"),
    "tree_sitter/queries": ("queries", "Query building", "AST query patterns"),
    "tree_sitter/transformers": ("transformers", "AST transformers", "AST transformation and visitors"),
    
    # model_ops
    "model_ops/datasets": ("datasets", "Dataset management", "Dataset handling"),
    "model_ops/evaluation": ("evaluation", "Model evaluation", "Evaluators and metrics"),
    "model_ops/fine_tuning": ("fine_tuning", "Fine-tuning", "Model fine-tuning"),
    "model_ops/training": ("training", "Training utilities", "Training loops and callbacks"),
    
    # deployment
    "deployment/strategies": ("strategies", "Deployment strategies", "Blue-green, canary, rolling"),
    "deployment/gitops": ("gitops", "GitOps integration", "Git-based deployments"),
    "deployment/manager": ("manager", "Deployment manager", "Core deployment management"),
    "deployment/rollback": ("rollback", "Rollback management", "Rollback and snapshots"),
    "deployment/health_checks": ("health_checks", "Health checks", "Probes and monitors"),
    
    # terminal_interface
    "terminal_interface/shells": ("shells", "Interactive shells", "Shell implementations"),
    "terminal_interface/utils": ("utils", "Terminal utilities", "Terminal helpers"),
    "terminal_interface/commands": ("commands", "Command registry", "Command definitions"),
    "terminal_interface/rendering": ("rendering", "Output rendering", "ANSI, tables, progress"),
    "terminal_interface/completions": ("completions", "Autocomplete", "Shell completions"),
}

def create_rasp_docs(subpath, name, title, desc):
    """Create RASP documentation for a submodule."""
    path = BASE / subpath
    path.mkdir(parents=True, exist_ok=True)
    
    # __init__.py
    init_content = f'''"""
{title} submodule.

{desc}
"""

__all__ = []
'''
    (path / "__init__.py").write_text(init_content)
    
    # README.md
    readme = f'''# {title.replace("_", " ").title()}

{desc}

## Overview

This submodule provides {title.lower()} functionality.

## Usage

```python
from codomyrmex.{subpath.replace("/", ".")} import ...
```
'''
    (path / "README.md").write_text(readme)
    
    # AGENTS.md
    agents = f'''# {title.replace("_", " ").title()} - Agent Instructions

## Purpose
{desc}

## Key Files
See module implementation files.

## Agent Guidelines
- Import from `codomyrmex.{subpath.replace("/", ".")}`
'''
    (path / "AGENTS.md").write_text(agents)
    
    # SPEC.md
    spec = f'''# {title.replace("_", " ").title()} - Technical Specification

## Overview
{desc}

## Architecture
See implementation files for detailed API.
'''
    (path / "SPEC.md").write_text(spec)
    
    # PAI.md
    pai = f'''# {title.replace("_", " ").title()} - PAI

## Path
`codomyrmex.{subpath.replace("/", ".")}`

## Purpose
{desc}
'''
    (path / "PAI.md").write_text(pai)
    
    print(f"Created RASP for {subpath}")

if __name__ == "__main__":
    for subpath, (name, title, desc) in SUBMODULES.items():
        create_rasp_docs(subpath, name, title, desc)
    print("Done!")
