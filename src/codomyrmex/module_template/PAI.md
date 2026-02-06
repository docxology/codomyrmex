# Personal AI Infrastructure — Module Template

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Module Template provides PAI integration patterns for creating new Codomyrmex modules.

## PAI Capabilities

### Standard Module Structure

Every module follows this structure:

```
my_module/
├── README.md      # Human documentation
├── AGENTS.md      # AI agent guidelines
├── SPEC.md        # Functional specification
├── PAI.md         # PAI integration (this file)
├── __init__.py    # Module exports
├── core.py        # Core implementation
└── tests/         # Module tests
```

### PAI Pattern Template

Standard PAI.md template:

```markdown
# Personal AI Infrastructure — [Module] Module

## Overview
Brief module description for AI context.

## PAI Capabilities
Working code examples.

## PAI Integration Points
Table of key components.
```

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
