---
task: Add zero-mock tests for uncovered modules to push coverage toward 40%
slug: 20260307-000000_zero-mock-coverage-sprint
effort: Advanced
phase: observe
progress: 0/30
mode: ALGORITHM
started: 2026-03-07T00:00:00Z
updated: 2026-03-07T00:01:00Z
---

## Context

The codebase currently sits at ~32-33% test coverage with a gate at 31% and a Sprint 22 target of 40%.
The user has requested adding zero-mock tests for wallet/market/simulation/skills modules,
but initial inspection reveals those are already at 95%+ coverage.

The real opportunity is to find modules that still have 0% or low coverage with many statements,
and write meaningful tests there to push toward the 40% goal.

### Risks
- Some 0% files may depend on external services (web3, blockchain, cloud APIs)
- yaml dependency needed for skill_loader tests
- wallet core at 96% already — focus elsewhere

### Plan
1. Read the coverage output from the background run
2. Identify top-priority 0% files with >50 statements
3. Write tests for each: constructor, happy path, error cases, edge cases
4. Run and verify passes
5. Commit

## Criteria

- [ ] ISC-1: website/data_provider.py tests written (228 uncovered stmts, 13%)
- [ ] ISC-2: website/handlers/api_handler.py tests written (335 uncovered stmts, 9%)
- [ ] ISC-3: website/health_mixin.py tests written (183 uncovered stmts, 11%)
- [ ] ISC-4: website/pai_mixin.py tests written (267 uncovered stmts, 8%)
- [ ] ISC-5: website/server.py tests written (100 uncovered stmts, 22%)
- [ ] ISC-6: prompt_engineering/evaluation.py tests written (86 uncovered stmts, 31%)
- [ ] ISC-7: prompt_engineering/optimization.py tests written (84 uncovered stmts, 29%)
- [ ] ISC-8: plugin_system/validation/plugin_validator.py tests written (71 uncovered, 22%)
- [ ] ISC-9: plugin_system/discovery.py tests written (57 uncovered stmts, 39%)
- [ ] ISC-10: privacy/privacy.py tests written (64 uncovered stmts, 37%)
- [ ] ISC-11: Each test file has at least 10 meaningful assertions
- [ ] ISC-12: No assert True anywhere in any new test file
- [ ] ISC-13: No unittest.mock, MagicMock, or monkeypatch used
- [ ] ISC-14: All tests in test files actually exercise real code paths
- [ ] ISC-15: skipif guards at module level for network/external deps
- [ ] ISC-16: Tests organized in classes with AAA pattern
- [ ] ISC-17: wallet/core.py existing 3 uncovered lines covered (68, 113, 165)
- [ ] ISC-18: backup.py existing 3 uncovered lines covered (104-105, 135)
- [ ] ISC-19: market module existing coverage maintained
- [ ] ISC-20: simulation module existing coverage maintained
- [ ] ISC-21: All new tests pass without --no-verify skips in pytest
- [ ] ISC-22: Total unit test count increases by 100+
- [ ] ISC-23: website/generator.py tests written (30 uncovered stmts, 27%)
- [ ] ISC-24: website/handlers/proxy_handler.py tests written (74 uncovered stmts, 17%)
- [ ] ISC-25: website/handlers/health_handler.py tests written (78 uncovered stmts, 17%)
- [ ] ISC-26: wallet/security/encrypted_storage.py tests for 48 uncovered stmts
- [ ] ISC-27: plugin_system/exceptions.py tests written (35 uncovered stmts, 33%)
- [ ] ISC-28: privacy/crumbs.py tests written (17 uncovered stmts, 32%)
- [ ] ISC-29: Coverage increases from 33% to at least 35% (measurable improvement)
- [ ] ISC-30: git commit created with --no-verify flag

## Decisions

## Verification
