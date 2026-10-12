# calendar_integration

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: August 2026

## Overview

Validation coverage, fixtures, and regression checks for Calendar Integration.

## Directory Contents

- `README.md` – File
- `SPEC.md` – File
- `test_calendar_models.py` – File
- `test_mcp_tools.py` – File

## Navigation

- **Parent Directory**: [integration](../README.md)
- **Project Root**: ../../../../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)

## Maintenance Notes

- Keep this document synchronized with adjacent source files.
- Update sibling README, AGENTS, and SPEC documents together.
- Preserve working examples when changing public behavior.
- Prefer measured validation output over inferred status claims.
- Record any remaining gaps in TODO.md or the nearest planning document.

## Credential and live-test boundaries

Default tests select missing temporary OAuth and ADC files and never probe an
operator token or call Google. Live tests require
`CODOMYRMEX_RUN_LIVE_CALENDAR_TESTS=1` before authentication. Event tests delete
their created event in `finally`; attendee injection additionally requires
`CODOMYRMEX_CALENDAR_TEST_ATTENDEE` to match the configured
`CODOMYRMEX_CALENDAR_ATTENDEE`. These opt-ins authorize account changes and
invitations and are not set by the default test run.
