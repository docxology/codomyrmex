# src/codomyrmex/build_synthesis/tests/unit

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Unit tests for the Build Synthesis module components. These tests ensure that individual templates are correctly rendered and that build profiles are accurately mapped to their respective configurations.

## Test Areas

- **Template Rendering**: Testing the `jinja2` logic for producing `SPEC.md` and `AGENTS.md` files.
- **Profile Validation**: Ensuring that 'debug' and 'release' profiles apply the correct compiler/linker flags.
- **Path Logic**: Testing relative path calculations for project-wide signposting.

## Navigation
- **Project Root**: [README](../../../../../README.md)
- **Parent Directory**: [tests](../README.md)
- **Src Hub**: [src](../../../../../src/README.md)