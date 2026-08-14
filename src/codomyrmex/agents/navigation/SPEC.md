# Agent Navigation — Specification

## Scope

`agents.navigation` is a read-only planning surface. It must be safe to call
before selecting an agent or tool and must not perform network requests,
credential probes, subprocess execution, or handler invocation.

## Record kinds

| Kind | Stable ID | Status meaning |
| --- | --- | --- |
| agent | `agent:<name>` | `declared` or `implementation_present`; not live health |
| module | `module:<name>` | filesystem/runtime package availability |
| tool | `tool:<qualified-name>` | discovered metadata; trust is descriptive |

Tool records are opt-in (`include_tools=True`) because dynamic MCP discovery can
import optional provider modules. Results are sorted by kind, name, and ID and
all list/search operations enforce a maximum result bound. Records include
machine-readable provenance describing whether they came from the registry,
filesystem, or static/dynamic MCP discovery. Provenance is metadata only and
never claims that a client was constructed or a service was reached.

Runtime inputs are fail-closed: limits must be integers, capability IDs must be
non-empty strings, and searches must contain searchable characters. A blank
search is not treated as an implicit list operation.

Documentation paths are emitted only when the corresponding file exists in the
checkout. Source paths are repository-relative when safely inside the checkout;
external or symlinked paths are represented by a bounded generic label rather
than leaking an absolute filesystem path. Bare-name lookups return no record
when ambiguous unless the caller supplies a kind.

## Failure behavior

Independent catalog sources fail soft. The response retains usable records and
returns source errors in the summary. A caller must treat `implementation_present`
as a discovery fact, not as authorization, successful construction, or endpoint
reachability. Summaries label an intact catalog `ready`, an empty catalog
`empty`, and a catalog with source errors `degraded`.
