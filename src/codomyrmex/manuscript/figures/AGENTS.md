# manuscript.figures — AGENTS.md

## Purpose

Figure generator modules and `_common.py` shared styling. See [../AGENTS.md](../AGENTS.md).

## Key Files

- `_common.py` — palettes, config loaders, `_save`, provenance helpers shared by every generator.
- `fig_*.py` — one module per figure.
- `orchestrator.py` — `main()`, runs every registered generator.
- `__init__.py` — `FIGURES` registry + re-exports.

## Dependencies

Depends on `codomyrmex.manuscript.variables` for computed token values consumed by
figure captions and analytical annotations. All figure metadata is sourced from the
`figures:` registry in `docs/manuscript/config.yaml`; do not duplicate filenames,
labels, widths, captions, thresholds, or experimental horizons in Markdown.

## Development Guidelines

- New figures get their own `fig_*.py` module and a `FIGURES` registry entry; do not grow `_common.py` into a second monolith.
- Scientific thresholds, horizons, score domains, and sampling parameters must come
  from the generated snapshot or the manuscript configuration. Geometry-only styling
  constants may remain local to a generator.
