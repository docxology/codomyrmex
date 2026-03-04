---
task: Write zero-mock unit tests for events module
slug: 20260304-120000_events-module-tests
effort: Advanced
phase: complete
progress: 28/28
mode: ALGORITHM
started: 2026-03-04T12:00:00
updated: 2026-03-04T12:00:00
---

## Context

Writing comprehensive zero-mock tests for the events module of Codomyrmex.

Key uncovered files:
- `dead_letter.py` — 0% (67 stmts): DeadLetter, DeadLetterQueue
- `replay.py` — 0% (68 stmts): StoredEvent, EventStore (file-backed)
- `mcp_tools.py` — 0% (43 stmts): emit_event, list_event_types, get_event_history
- `integration_bus.py` — 0% (51 stmts): needs investigation
- `core/mixins.py` — 46%: EventMixin init_events, emit, on, off, cleanup_events
- `handlers/event_logger.py` — 51%: export_logs, get_events, get_error_events, clear, perf report
- `streaming/async_stream.py` — 0% (136 stmts): needs investigation

Policy: Zero mocks. Use tmp_path for file I/O. Real classes only.

### Risks
- Singleton buses (`get_event_bus`, `get_event_logger`) carry state between tests
- File-backed EventStore/DeadLetterQueue need tmp_path
- async_stream.py may have complex asyncio requirements

## Criteria

- [x] ISC-1: TestEventMixin.test_init_events_sets_source covers init_events()
- [x] ISC-2: TestEventMixin.test_emit_publishes_to_bus covers emit()
- [x] ISC-3: TestEventMixin.test_on_subscribes_and_stores_id covers on()
- [x] ISC-4: TestEventMixin.test_off_unsubscribes covers off()
- [x] ISC-5: TestEventMixin.test_cleanup_events_removes_all covers cleanup_events()
- [x] ISC-6: TestEventMixin.test_event_bus_property_lazy_init covers lazy bus property
- [x] ISC-7: TestDeadLetterQueue.test_enqueue_writes_to_file covers enqueue()
- [x] ISC-8: TestDeadLetterQueue.test_list_all_returns_letters covers list_all()
- [x] ISC-9: TestDeadLetterQueue.test_purge_clears_queue covers purge()
- [x] ISC-10: TestDeadLetterQueue.test_retry_all_success covers retry_all() success
- [x] ISC-11: TestDeadLetterQueue.test_retry_all_failure covers retry_all() failure
- [x] ISC-12: TestDeadLetterQueue.test_count_property covers count property
- [x] ISC-13: TestFileBackedEventStore.test_append_writes_events covers append()
- [x] ISC-14: TestFileBackedEventStore.test_replay_calls_handler covers replay()
- [x] ISC-15: TestFileBackedEventStore.test_replay_from_sequence covers from_sequence filter
- [x] ISC-16: TestFileBackedEventStore.test_replay_event_type_filter covers event_types filter
- [x] ISC-17: TestFileBackedEventStore.test_snapshot_and_load covers snapshot/load_snapshot
- [x] ISC-18: TestFileBackedEventStore.test_event_count_property covers event_count
- [x] ISC-19: TestMcpEmitEvent.test_emit_known_event_type covers emit_event() with known type
- [x] ISC-20: TestMcpEmitEvent.test_emit_unknown_falls_back_to_custom covers unknown type fallback
- [x] ISC-21: TestMcpEmitEvent.test_emit_returns_event_id covers event_id in response
- [x] ISC-22: TestMcpListEventTypes.test_list_returns_dict covers list_event_types()
- [x] ISC-23: TestMcpGetEventHistory.test_get_history_returns_events covers get_event_history()
- [x] ISC-24: TestEventLoggerExtended.test_export_logs_json covers export_logs() JSON
- [x] ISC-25: TestEventLoggerExtended.test_export_logs_csv covers export_logs() CSV
- [x] ISC-26: TestEventLoggerExtended.test_get_error_events covers get_error_events()
- [x] ISC-27: TestEventLoggerExtended.test_clear_resets_all covers clear()
- [x] ISC-28: TestEventLoggerExtended.test_get_performance_report covers get_performance_report()

## Decisions

## Verification
