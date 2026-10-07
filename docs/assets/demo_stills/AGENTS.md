# AGENTS.md — `codomyrmex/docs/assets/demo_stills`

## Purpose

Six demo still frames (`still_01.png` … `still_06.png`) captured from demo runs
for use in documentation and the generated website.

## Key Files

- `still_01.png` … `still_06.png` — 3840×2160 RGB PNG frames, between about
  0.45 MB and 1.05 MB each (about 5 MB for the set).
- [`README.md`](README.md) — human signpost.

## Dependencies

- Published by MkDocs: [`mkdocs.yml`](../../../mkdocs.yml) uses the default
  `docs/` source directory, so these files are copied into the built site under
  `assets/demo_stills/`.
- [`scripts/rasp_gap_report.py`](../../../scripts/rasp_gap_report.py) excludes
  this image-only tree from the RASP documentation gap scan.
- No Markdown page in the repository currently embeds these frames; search for
  `demo_stills/` before assuming a frame is unused or safe to rename.
- Parent: [../README.md](../README.md) · Sibling assets: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- Regenerate or re-capture stills rather than editing images in place; no
  in-repo script produces them, so replace a frame with a new capture at the
  same name and resolution.
- Keep filenames stable once a page links a frame.
- Compress before adding frames; the published site ships every file here.
