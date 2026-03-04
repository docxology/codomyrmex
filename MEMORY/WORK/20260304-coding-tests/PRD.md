---
task: Write comprehensive zero-mock unit tests for coding module
slug: 20260304-coding-tests
effort: Advanced
phase: complete
progress: 32/32
mode: ALGORITHM
started: 2026-03-04T05:19:00
updated: 2026-03-04T05:19:00
---

## Context

The coding module at `src/codomyrmex/coding/` has 49 open desloppify test_coverage gaps with only 6 existing test files. This is the worst coverage ratio in the project.

Target: 50+ new test methods across multiple classes exercising:
- `execution/` submodule (validate_timeout, validate_language, validate_session_id, SUPPORTED_LANGUAGES)
- `debugging/` submodule (ErrorDiagnosis dataclass, FixVerifier, PatchGenerator._construct_prompt, Debugger)
- `sandbox/` submodule (ExecutionLimits, prepare_code_file, prepare_stdin_file, cleanup_temp_files, resource_limits_context)
- `monitoring/` submodule (ResourceMonitor, MetricsCollector, ExecutionMonitor)
- `generator.py` (CodeBundle, CodeGenerator)
- `exceptions.py` (all custom exceptions)
- `mcp_tools.py` (code_execute, code_list_languages, code_review_file, code_review_project, code_debug)

Zero-mock policy: NO unittest.mock, MagicMock, patch, monkeypatch — EVER.

### Risks
- Docker-requiring tests (execute_code calls check_docker_available) — test the non-Docker paths only
- Some modules have complex dependencies (agents/llm_client in PatchGenerator) — test with llm_client=None
- resource_limits_context uses OS-level rlimit syscalls — must use real context managers

## Criteria

- [x] ISC-1: TestExecutionLanguageSupport class has at least 5 test methods
- [x] ISC-2: validate_language returns True for all 8 supported languages
- [x] ISC-3: validate_language returns False for unsupported languages
- [x] ISC-4: SUPPORTED_LANGUAGES dict has expected keys and sub-fields
- [x] ISC-5: TestValidateTimeout class tests default, minimum clamp, maximum clamp, None input
- [x] ISC-6: validate_timeout(None) returns DEFAULT_TIMEOUT (30)
- [x] ISC-7: validate_timeout(0) returns MIN_TIMEOUT (1)
- [x] ISC-8: validate_timeout(9999) returns MAX_TIMEOUT (300)
- [x] ISC-9: TestValidateSessionId class tests valid IDs, None, too-long, special chars
- [x] ISC-10: validate_session_id(None) returns None
- [x] ISC-11: validate_session_id with special chars returns None
- [x] ISC-12: validate_session_id with 65+ char string returns None
- [x] ISC-13: TestExecutionLimits class tests defaults, validation, invalid values
- [x] ISC-14: ExecutionLimits() uses correct defaults (30s, 256MB, 0.5 CPU)
- [x] ISC-15: ExecutionLimits with time_limit=0 raises ValueError
- [x] ISC-16: ExecutionLimits with cpu_limit=5.0 raises ValueError
- [x] ISC-17: TestSandboxSecurity class tests prepare_code_file, prepare_stdin_file, cleanup_temp_files
- [x] ISC-18: prepare_code_file creates real file with correct extension
- [x] ISC-19: prepare_stdin_file returns None for empty/None stdin
- [x] ISC-20: cleanup_temp_files removes the temp directory
- [x] ISC-21: TestResourceMonitor tests start_monitoring, get_resource_usage
- [x] ISC-22: ResourceMonitor.get_resource_usage returns dict with all expected keys
- [x] ISC-23: TestMetricsCollector tests record_execution, get_summary, clear, get_language_stats
- [x] ISC-24: MetricsCollector.get_summary returns zeros when empty
- [x] ISC-25: MetricsCollector.record_execution and get_language_stats group by language
- [x] ISC-26: TestExecutionMonitor tests start_execution, end_execution, get_execution_stats
- [x] ISC-27: ExecutionMonitor.get_execution_stats returns zeros when no executions
- [x] ISC-28: TestCodeGenerator tests generate with class spec, function spec, no-ops spec
- [x] ISC-29: CodeGenerator.generate returns CodeBundle with correct language and filename
- [x] ISC-30: TestCodeBundle tests line_count property and to_dict method
- [x] ISC-31: TestCodingExceptions tests all 10 custom exception classes
- [x] ISC-32: TestMcpTools tests code_list_languages and code_execute with unsupported language

## Decisions

## Verification

- 270 new test methods across 6 new test files, 33 test classes
- All 270 tests pass (915 total in coding module, 18 skipped legitimate)
- Zero assert True, zero mocks, zero monkeypatch
- ISC-1 through ISC-32: all 32 criteria satisfied
- Files: test_execution_core.py (59), test_sandbox_security.py (34), test_generator_module.py (42), test_coding_exceptions.py (56), test_mcp_tools_coding.py (38), test_debugging_extended.py (41)
