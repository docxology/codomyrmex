# UOR — Universal Object Reference

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Universal Object Reference submodule integrating [UOR Foundation](https://github.com/UOR-Foundation) concepts into the relations module. Provides content-addressed entity identity using PRISM triadic coordinates over the modular ring Z/(2^n)Z.

**Key Concepts:**

- **PRISM Coordinates** — Every digital value gets a unique triadic coordinate (datum, stratum, spectrum) derived from its intrinsic structure
- **Content-Addressed Identity** — Entity identity determined by SHA256 of intrinsic attributes, not by storage location
- **Derivation Tracking** — Provenance certificates for all entity operations

## Quick Start

```python
from codomyrmex.relations.uor import PrismEngine, EntityManager, UORGraph

# PRISM Engine — triadic coordinates
engine = PrismEngine(quantum=0)  # 8-bit, 256 states
engine.verify()  # confirms algebraic coherence

t = engine.triad(42)
# t.datum = (42,), t.stratum = (3,), t.spectrum = ((1, 3, 5),)

engine.correlate(42, 43)["fidelity"]  # 0.875

# Entity Management
mgr = EntityManager()
e1 = mgr.add_entity("Alice", "person", {"role": "engineer"})
e2 = mgr.add_entity("Bob", "person", {"role": "designer"})
similar = mgr.find_similar(e1.id)

# Content-Addressed Graph
graph = UORGraph()
a = graph.add_entity("Module A", "component")
b = graph.add_entity("Module B", "component")
graph.add_relationship(a.id, b.id, "depends_on")
path = graph.find_path(a.id, b.id)
```

## References

- [UOR Foundation](https://github.com/UOR-Foundation)
- [PRISM](https://github.com/UOR-Foundation/prism) — Universal coordinate system for information
- [UOR-Framework](https://github.com/UOR-Foundation/UOR-Framework) — Formalization of UOR model

## Navigation

- [SPEC](SPEC.md) | [API](API_SPECIFICATION.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md) | [Parent](../README.md)
