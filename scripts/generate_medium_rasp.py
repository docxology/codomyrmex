#!/usr/bin/env python3
"""
Batch generate RASP documentation for medium-priority submodules.
"""

import os
from pathlib import Path

BASE = Path("/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex")

# Define all medium-priority submodules
SUBMODULES = {
    # llm
    "llm/providers": ("providers", "LLM Providers", "Provider abstractions for OpenAI, Anthropic, Google"),
    "llm/chains": ("chains", "Reasoning Chains", "Chain-of-thought and reasoning chains"),
    "llm/memory": ("memory", "Conversation Memory", "Context and conversation memory management"),
    "llm/tools": ("tools", "Tool Calling", "Tool calling framework for LLMs"),
    
    # api
    "api/versioning": ("versioning", "API Versioning", "API version management"),
    "api/rate_limiting": ("rate_limiting", "Rate Limiting", "Rate limiters and quotas"),
    "api/authentication": ("authentication", "Authentication", "Auth middleware and tokens"),
    "api/graphql": ("graphql", "GraphQL", "GraphQL schema and resolvers"),
    
    # cli
    "cli/parsers": ("parsers", "Argument Parsers", "Argument parsing utilities"),
    "cli/formatters": ("formatters", "Output Formatters", "JSON, table, and text formatters"),
    "cli/completions": ("completions", "Shell Completions", "Bash/zsh completion generators"),
    "cli/themes": ("themes", "CLI Themes", "Color themes for CLI output"),
    
    # cache
    "cache/policies": ("policies", "Eviction Policies", "LRU, LFU, TTL eviction"),
    "cache/invalidation": ("invalidation", "Cache Invalidation", "Invalidation strategies"),
    "cache/distributed": ("distributed", "Distributed Cache", "Redis cluster support"),
    "cache/serializers": ("serializers", "Cache Serializers", "Custom serialization"),
    
    # cloud common
    "cloud/common": ("common", "Cloud Common", "Shared cloud utilities"),
    
    # cloud aws
    "cloud/aws/storage": ("storage", "AWS Storage", "S3 object storage"),
    "cloud/aws/compute": ("compute", "AWS Compute", "EC2 and container instances"),
    "cloud/aws/serverless": ("serverless", "AWS Serverless", "Lambda functions"),
    
    # cloud azure
    "cloud/azure/storage": ("storage", "Azure Storage", "Blob storage"),
    "cloud/azure/compute": ("compute", "Azure Compute", "VM and AKS"),
    "cloud/azure/serverless": ("serverless", "Azure Serverless", "Azure Functions"),
    
    # cloud gcp
    "cloud/gcp/storage": ("storage", "GCP Storage", "Cloud Storage"),
    "cloud/gcp/compute": ("compute", "GCP Compute", "GCE and GKE"),
    "cloud/gcp/serverless": ("serverless", "GCP Serverless", "Cloud Run and Functions"),
    
    # spatial
    "spatial/coordinates": ("coordinates", "Coordinate Systems", "Coordinate transforms"),
    "spatial/rendering": ("rendering", "Spatial Rendering", "Visualization backends"),
    "spatial/physics": ("physics", "Physics Simulation", "Physics utilities"),
    
    # fpf
    "fpf/reasoning": ("reasoning", "First-Principles Reasoning", "Reasoning engine"),
    "fpf/optimization": ("optimization", "Constraint Optimization", "Optimization solvers"),
    "fpf/constraints": ("constraints", "Constraint Definitions", "Constraint types"),
    "fpf/models": ("models", "Domain Models", "Domain model definitions"),
    
    # coding
    "coding/refactoring": ("refactoring", "Code Refactoring", "Refactoring tools"),
    "coding/generation": ("generation", "Code Generation", "Generation utilities"),
    "coding/testing": ("testing", "Test Tools", "Test generation and execution"),
    "coding/analysis": ("analysis", "Code Analysis", "Analysis tools"),
    
    # orchestrator
    "orchestrator/engines": ("engines", "Orchestration Engines", "Core execution engines"),
    "orchestrator/schedulers": ("schedulers", "Task Schedulers", "Scheduling algorithms"),
    "orchestrator/workflows": ("workflows", "Workflow Definitions", "Workflow management"),
    "orchestrator/monitors": ("monitors", "Execution Monitors", "Progress monitoring"),
    
    # logistics
    "logistics/routing": ("routing", "Task Routing", "Routing algorithms"),
    "logistics/optimization": ("optimization", "Schedule Optimization", "Optimization solvers"),
    "logistics/resources": ("resources", "Resource Allocation", "Resource management"),
    "logistics/tracking": ("tracking", "Progress Tracking", "Status tracking"),
    
    # skills
    "skills/discovery": ("discovery", "Skill Discovery", "Skill indexing and discovery"),
    "skills/execution": ("execution", "Skill Execution", "Runtime execution"),
    "skills/composition": ("composition", "Skill Composition", "Composition patterns"),
    "skills/testing": ("testing", "Skill Testing", "Testing framework"),
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
