<!-- agents: curated -->

# Local verification scope

## Purpose

Verify dependency ordering using the checked-in sorting helper and a finite fictional fixture.

## Key Files

The [verification guide](README.md) describes the graph, replay, and renderer. The [specification](SPEC.md) records the acceptance conditions. The `tests/unit/utils/reader-*.in` files are staged in a disposable Template project for PDF and HTML rendering.

## Dependencies

The scoped run uses pytest, Matplotlib, and the pinned Template renderer. The sparse checkout isolates the standard-library graph utility.

## Development Guidelines

Keep the fixture and its generated reference image in sync. Leave the original manuscript and publishing process under their existing ownership. Record the verification result through the local test and renderer receipts.

## Navigation

- [Verification guide](README.md)
- [Documentation instructions](../AGENTS.md)
- [Repository README](../../README.md)
