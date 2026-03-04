---
task: "Write comprehensive zero-mock unit tests for LLM module"
slug: "20260304-llm-unit-tests"
effort: Advanced
phase: complete
progress: 45/45
mode: ALGORITHM
started: "2026-03-04T00:00:00"
updated: "2026-03-04T00:00:00"
---

## Context

Expanding test coverage for `src/codomyrmex/llm/` module. Current coverage is low on key submodules:
- `providers/base.py` — 0% (17 stmts)
- `providers/factory.py` — 0% (14 stmts)
- `providers/anthropic.py` — 0% (54 stmts)
- `providers/openai.py` — 0% (43 stmts)
- `providers/openrouter.py` — 0% (45 stmts)
- `mcp_tools.py` — 0% (54 stmts)
- `safety.py` — 51% (81 stmts)
- `fabric/fabric_config_manager.py` — 58% (48 stmts)
- `fabric/fabric_manager.py` — 41% (64 stmts)
- `fabric/fabric_orchestrator.py` — 25% (60 stmts)
- `multimodal/models.py` — 57% (122 stmts)
- `router.py` — 58% (170 stmts)
- `exceptions.py` — 76% (95 stmts)

Zero-mock policy: no unittest.mock, MagicMock, patch. Real code paths only. Skip guards for external services.

### Risks
- Provider tests require openai/anthropic packages installed
- Fabric binary tests require subprocess calls
- MCP tool tests trigger real imports

## Criteria

- [ ] ISC-1: `providers/models.py` Message.to_dict() includes optional fields when set
- [ ] ISC-2: `providers/models.py` Message.to_dict() omits None optional fields
- [ ] ISC-3: `providers/models.py` CompletionResponse.total_tokens returns usage sum
- [ ] ISC-4: `providers/models.py` CompletionResponse.total_tokens returns 0 when no usage
- [ ] ISC-5: `providers/models.py` ProviderType enum has all expected string values
- [ ] ISC-6: `providers/models.py` ProviderConfig defaults are correct (timeout=60, retries=3)
- [ ] ISC-7: `providers/base.py` LLMProvider context manager calls cleanup on exit
- [ ] ISC-8: `providers/base.py` LLMProvider.get_model returns provided model if given
- [ ] ISC-9: `providers/base.py` LLMProvider.get_model returns default_model from config if model=None
- [ ] ISC-10: `providers/factory.py` get_provider raises ValueError for unsupported type
- [ ] ISC-11: `providers/factory.py` get_provider creates ProviderConfig from kwargs when config=None
- [ ] ISC-12: `providers/openrouter.py` FREE_MODELS list is non-empty
- [ ] ISC-13: `providers/openrouter.py` OpenRouterProvider sets base_url to BASE_URL when not specified
- [ ] ISC-14: `providers/openrouter.py` OpenRouterProvider.list_models returns FREE_MODELS
- [ ] ISC-15: `providers/openrouter.py` OpenRouterProvider._default_model returns "openrouter/free"
- [ ] ISC-16: `providers/anthropic.py` AnthropicProvider.list_models returns claude models
- [ ] ISC-17: `providers/anthropic.py` AnthropicProvider._default_model returns claude-3-5-sonnet
- [ ] ISC-18: `safety.py` SafetyFilter detects email address as PII violation
- [ ] ISC-19: `safety.py` SafetyFilter detects SSN pattern as critical violation
- [ ] ISC-20: `safety.py` SafetyFilter detects credit card as critical violation
- [ ] ISC-21: `safety.py` SafetyFilter detects prompt injection patterns
- [ ] ISC-22: `safety.py` SafetyFilter detects dangerous code execution patterns
- [ ] ISC-23: `safety.py` SafetyFilter.check returns safe report for clean text
- [ ] ISC-24: `safety.py` SafetyFilter sanitizes redactable violations from text
- [ ] ISC-25: `safety.py` SafetyReport.critical_violations filters by severity
- [ ] ISC-26: `fabric/fabric_config_manager.py` FabricPattern dataclass stores fields correctly
- [ ] ISC-27: `fabric/fabric_config_manager.py` FabricConfigManager returns empty config without file
- [ ] ISC-28: `fabric/fabric_config_manager.py` FabricConfigManager.add_pattern stores pattern by name
- [ ] ISC-29: `fabric/fabric_config_manager.py` FabricConfigManager.list_patterns returns added patterns
- [ ] ISC-30: `multimodal/models.py` MediaContent.size_bytes returns len of data
- [ ] ISC-31: `multimodal/models.py` MediaContent.hash returns 16-char hex string
- [ ] ISC-32: `multimodal/models.py` MediaContent.to_base64 round-trips correctly
- [ ] ISC-33: `multimodal/models.py` MediaContent.from_base64 reconstructs data correctly
- [ ] ISC-34: `multimodal/models.py` ImageContent.aspect_ratio returns width/height
- [ ] ISC-35: `multimodal/models.py` ImageContent.aspect_ratio returns 0 when height is 0
- [ ] ISC-36: `multimodal/models.py` MultimodalMessage.add_text sets text field
- [ ] ISC-37: `multimodal/models.py` MultimodalMessage.has_images detects image content
- [ ] ISC-38: `multimodal/models.py` MultimodalMessage.to_dict includes text part
- [ ] ISC-39: `exceptions.py` LLMConnectionError stores provider and endpoint in context
- [ ] ISC-40: `exceptions.py` LLMRateLimitError stores retry_after in context
- [ ] ISC-41: `exceptions.py` ResponseParsingError truncates long raw_response
- [ ] ISC-42: `exceptions.py` ContextWindowError stores all context fields
- [ ] ISC-43: `mcp_tools.py` MCP tool metadata exposed via _mcp_tool_meta attribute
- [ ] ISC-44: 40+ new test methods total across all new test files
- [ ] ISC-45: All new tests pass with zero failures

## Decisions

- Concrete stub classes replace missing SDK clients for provider tests (e.g. OpenAI not installed = _client is None → test the RuntimeError path)
- Safety tests use literal text strings with real patterns — no mocking of regex
- FabricConfigManager tested with tmp_path (real filesystem, no stubs)

## Verification

- ISC-1 to ISC-6: Message/CompletionResponse/ProviderType/ProviderConfig tested — all pass in TestMessageDataclass, TestCompletionResponse, TestProviderTypeEnum, TestProviderConfig
- ISC-7 to ISC-9: LLMProvider context manager and get_model tested in TestLLMProviderBase — all pass
- ISC-10 to ISC-11: Factory ValueError and kwargs-config tested in TestProviderFactory — all pass
- ISC-12 to ISC-17: OpenRouterProvider FREE_MODELS, base_url, list_models, _default_model; AnthropicProvider list_models, _default_model tested — all pass
- ISC-18 to ISC-25: Safety PII/injection/code/sanitize/report tests — all pass. safety.py now 100%
- ISC-26 to ISC-29: FabricConfigManager pattern/config tests — all pass. fabric_config_manager.py now 90%
- ISC-30 to ISC-38: MultimodalMessage/MediaContent/ImageContent tests — all pass. multimodal/models.py now 84%
- ISC-39 to ISC-42: Exception context storage tests — all pass. exceptions.py now 100%
- ISC-43: MCP tool _mcp_tool_meta verified for all 4 tools — all pass
- ISC-44: 154 new test methods total (exceeds 40 minimum)
- ISC-45: 590 passed, 10 skipped, 0 failed

Coverage improvements:
  providers/base.py: 0% → 100%
  providers/factory.py: 0% → 100%
  providers/models.py: 100% (confirmed)
  providers/openai.py: 0% → 56%
  providers/openrouter.py: 0% → 62%
  providers/anthropic.py: 0% → 43%
  exceptions.py: 76% → 100%
  safety.py: 51% → 100%
  fabric/fabric_config_manager.py: 58% → 90%
  multimodal/models.py: 57% → 84%
  mcp_tools.py: 0% → 24%
  router.py: 58% → 61%
