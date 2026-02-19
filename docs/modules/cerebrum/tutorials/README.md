# Cerebrum Tutorials

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Step-by-step tutorials for using the Cerebrum cognitive architecture module.

## Available Tutorials

| Tutorial | Description |
|----------|-------------|
| [Getting Started](#getting-started) | Basic setup and first reasoning chain |
| [Working Memory](#working-memory) | Managing context with working memory |
| [Decision Making](#decision-making) | Using the decision module |

## Getting Started

```python
from codomyrmex.cerebrum import CerebrumEngine, ReasoningChain

# Initialize engine
engine = CerebrumEngine()

# Create reasoning chain
chain = ReasoningChain()
chain.add_step("Analyze the problem")
chain.add_step("Generate solutions")
chain.add_step("Evaluate and select")

result = chain.execute(context)
```

## Working Memory

```python
from codomyrmex.cerebrum import WorkingMemory

memory = WorkingMemory()
memory.store("goal", "Refactor authentication")
memory.store("constraints", ["backward compatible"])

# Retrieve context
goal = memory.retrieve("goal")
```

## Navigation

- **Parent**: [Cerebrum Documentation](../README.md)
- **Source**: [src/codomyrmex/cerebrum/](../../../../src/codomyrmex/cerebrum/)
