---
task: "Add zero-mock tests for networking/deployment/model_ops"
slug: "20260307-000000_zero-mock-tests-networking-deployment-modelops"
effort: Advanced
phase: complete
progress: 24/24
mode: ALGORITHM
started: "2026-03-07T00:00:00Z"
updated: "2026-03-07T00:00:00Z"
---

## Context

Three codomyrmex modules (networking, deployment, model_ops) have 0% or very low test coverage. The task is to write 40-60 zero-mock tests per module, following the strict zero-mock policy (no MagicMock, no monkeypatch, no unittest.mock). External dependencies are guarded by @pytest.mark.skipif. Tests must call real code with real in-memory data and pass before commit.

### Risks
- Source files may have complex constructor signatures requiring careful reading
- Some modules may import heavy external deps (boto3, torch, etc.) — need skipif guards
- Existing test infrastructure (conftest.py, pytest.ini markers) must be respected
- Coverage gate is 31% — new tests must not break collection

## Criteria

- [ ] ISC-1: networking/models.py source read, public API understood
- [ ] ISC-2: networking/protocols.py source read, public API understood
- [ ] ISC-3: networking/validators.py source read, public API understood
- [ ] ISC-4: deployment/manager.py source read, public API understood
- [ ] ISC-5: deployment/models.py source read, public API understood
- [ ] ISC-6: deployment/strategies.py source read, public API understood
- [ ] ISC-7: model_ops/availability.py source read, public API understood
- [ ] ISC-8: model_ops/fine_tuning/fine_tuning.py source read, public API understood
- [ ] ISC-9: model_ops/mcp_tools.py source read, public API understood
- [ ] ISC-10: test_networking_core.py written with 40+ tests organized in classes
- [ ] ISC-11: test_networking_core.py has no mocks/monkeypatch/MagicMock
- [ ] ISC-12: test_networking_core.py skipif guards for network-dependent code
- [ ] ISC-13: test_deployment_core.py written with 40+ tests organized in classes
- [ ] ISC-14: test_deployment_core.py has no mocks/monkeypatch/MagicMock
- [ ] ISC-15: test_deployment_core.py in-memory simulation only
- [ ] ISC-16: test_model_ops_core.py written with 40+ tests organized in classes
- [ ] ISC-17: test_model_ops_core.py has no mocks/monkeypatch/MagicMock
- [ ] ISC-18: test_model_ops_core.py skipif guards for model server deps
- [ ] ISC-19: uv run pytest test_networking_core.py -q passes (0 failures)
- [ ] ISC-20: uv run pytest test_deployment_core.py -q passes (0 failures)
- [ ] ISC-21: uv run pytest test_model_ops_core.py -q passes (0 failures)
- [ ] ISC-22: git commit created with all 3 test files --no-verify
- [ ] ISC-23: coverage for networking module measured and reported
- [ ] ISC-24: coverage for deployment and model_ops measured and reported

## Decisions

## Verification
