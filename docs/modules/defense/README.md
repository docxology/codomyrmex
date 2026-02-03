# Defense Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Secure Cognitive Agent module for active defense against cognitive attacks. Shifts security from passive filtering to active countermeasures.

## Key Features

- **Exploit Detection**: Pattern-based attack identification
- **Context Poisoning**: Inject false context to mislead attackers
- **Rabbit Hole**: Engage attackers in endless diversionary loops

## Key Classes

| Class | Description |
|-------|-------------|
| `ActiveDefense` | Core defense system |
| `RabbitHole` | Attacker engagement |
| `ContextPoisoner` | False context injection |
| `ExploitDetector` | Attack detection |

## Quick Start

```python
from codomyrmex.defense import ActiveDefense

defense = ActiveDefense()
if defense.detect_exploit(user_input):
    context = defense.poison_context(attacker_id="unknown", intensity=0.8)
```

## Related Modules

- [identity](../identity/) - Persona verification
- [wallet](../wallet/) - Key protection
- [privacy](../privacy/) - Data minimization

## Navigation

- **Source**: [src/codomyrmex/defense/](../../../src/codomyrmex/defense/)
- **Parent**: [docs/modules/](../README.md)
