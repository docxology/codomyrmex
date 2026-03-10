# Codomyrmex Agents — src/codomyrmex/tests/unit/llm

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Test files and validation suites.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `chains/` – Directory containing chains components
- `cost_tracking/` – Directory containing cost_tracking components
- `embeddings/` – Directory containing embeddings components
- `examples/` – Directory containing examples components
- `guardrails/` – Directory containing guardrails components
- `ollama_test_helpers.py` – Project file
- `rag/` – Directory containing rag components
- `streaming/` – Directory containing streaming components
- `test_chain_of_thought.py` – Project file
- `test_config.py` – Project file
- `test_context_manager.py` – Project file
- `test_gemini_provider.py` – Project file
- `test_guardrails_detectors.py` – Project file
- `test_llm.py` – Project file
- `test_llm_base.py` – Project file
- `test_llm_exceptions.py` – Project file
- `test_llm_exceptions_direct.py` – Project file
- `test_multimodal_models.py` – Project file
- `test_ollama_integration.py` – Project file
- `test_openrouter_provider.py` – Project file
- `test_output_manager.py` – Project file
- `test_provider_models.py` – Project file
- `test_providers.py` – Project file
- `test_reasoning_models.py` – Project file
- `test_router.py` – Project file
- `test_safety_fabric_multimodal.py` – Project file

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `PAI.md`
- `README.md`
- `SPEC.md`
- `__init__.py`
- `ollama_test_helpers.py`
- `test_chain_of_thought.py`
- `test_config.py`
- `test_context_manager.py`
- `test_gemini_provider.py`
- `test_guardrails_detectors.py`
- `test_llm.py`
- `test_llm_base.py`
- `test_llm_exceptions.py`
- `test_llm_exceptions_direct.py`
- `test_multimodal_models.py`
- `test_ollama_integration.py`
- `test_openrouter_provider.py`
- `test_output_manager.py`
- `test_provider_models.py`
- `test_providers.py`
- `test_reasoning_models.py`
- `test_router.py`
- `test_safety_fabric_multimodal.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [unit](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../../README.md - Main project documentation
