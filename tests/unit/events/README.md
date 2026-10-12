# events

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: August 2026

## Overview

Validation coverage, fixtures, and regression checks for Events.

## Directory Contents

- `PAI.md` – File
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `test_async_events.py` – File
- `test_core_exceptions.py` – File
- `test_event_bus.py` – File
- `test_event_emitter.py` – File
- `test_event_exceptions.py` – File
- `test_event_schema.py` – File
- `test_event_streaming.py` – File
- `test_event_system_review.py` – File
- `test_events.py` – File
- `test_events_comprehensive.py` – File
- `test_events_core.py` – File
- `test_hypothesis_events.py` – File
- `test_mcp_tools.py` – File
- `test_zero_mock.py` – File

## Navigation

- **Parent Directory**: [unit](../README.md)
- **Project Root**: ../../../../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)

## One-time listener controls

`test_event_system_review.py` verifies atomic one-time dispatch with real concurrent publishers, queued async wrappers, and recursive publication. Async signals use the owning loop's `call_soon_threadsafe`; a single-worker completion fence replaces timing sleeps.
