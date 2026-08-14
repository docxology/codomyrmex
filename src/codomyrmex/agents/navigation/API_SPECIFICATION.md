# Agent Navigation — API Specification

```python
from codomyrmex.agents.navigation import (
    CapabilityCatalog,
    CapabilityRecord,
    build_capability_catalog,
)
```

`build_capability_catalog(include_tools=False)` returns a
`CapabilityCatalog`. Its `list()`, `find()`, `get()`, `search()`, and `summary()` methods
are deterministic and JSON-safe through `CapabilityRecord.to_dict()`. Serialized
records contain a `provenance` object identifying the metadata source and a
`details` object normalized to strict JSON-compatible values.

`find()` returns all exact or bare-name matches. `get()` returns a record only
when the ID or bare name is unambiguous; pass `kind="agent"`, `"module"`, or
`"tool"` to resolve a shared bare name safely. Documentation fields are
source-bound: missing files are represented as `null`, never as a claimed path.

Public methods reject malformed limits, IDs, and search queries with
`ValueError`; callers should not rely on implicit string or numeric coercion.
`summary()` reports `catalog_state` as `ready`, `empty`, or `degraded`.

The catalog does not attach callable handlers to records and does not run
health probes. Use the agent setup registry or the relevant provider client for
those actions.
