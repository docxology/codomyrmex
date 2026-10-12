# calendar_integration

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: August 2026

## Overview

Validation coverage, fixtures, and regression checks for Calendar Integration.

## Directory Contents

- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `test_calendar.py` – File
- `test_mcp_tools.py` – File
- `conftest.py` — Isolated OAuth and ADC paths without changing HOME
- `test_auth_isolation.py` — Real selected token files and local Google transports

## Navigation

- **Parent Directory**: [unit](../README.md)
- **Project Root**: ../../../../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)

## Authentication controls

Default tests remove OAuth environment inputs and select nonexistent temporary
`GOOGLE_CALENDAR_TOKEN_FILE` and `GOOGLE_APPLICATION_CREDENTIALS` paths. They
exercise real authentication failure without operator token, gcloud, or metadata
fallback. Positive token tests build and close the actual Google transport with
synthetic local credentials; no API request or live account acceptance occurs.
Live reads require `CODOMYRMEX_RUN_LIVE_CALENDAR_TESTS=1` explicitly.
