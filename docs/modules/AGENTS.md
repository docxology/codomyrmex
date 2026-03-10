# Codomyrmex Agents — docs/modules

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Documentation files and guides.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `agentic_memory/` – Directory containing agentic_memory components
- `agents/` – Directory containing agents components
- `ai_gateway/` – Directory containing ai_gateway components
- `aider/` – Directory containing aider components
- `api/` – Directory containing api components
- `audio/` – Directory containing audio components
- `auth/` – Directory containing auth components
- `autograd/` – Directory containing autograd components
- `bio_simulation/` – Directory containing bio_simulation components
- `cache/` – Directory containing cache components
- `calendar_integration/` – Directory containing calendar_integration components
- `cerebrum/` – Directory containing cerebrum components
- `ci_cd_automation/` – Directory containing ci_cd_automation components
- `cli/` – Directory containing cli components
- `cloud/` – Directory containing cloud components
- `coding/` – Directory containing coding components
- `collaboration/` – Directory containing collaboration components
- `compression/` – Directory containing compression components
- `concurrency/` – Directory containing concurrency components
- `config_audits/` – Directory containing config_audits components
- `config_management/` – Directory containing config_management components
- `config_monitoring/` – Directory containing config_monitoring components
- `container_optimization/` – Directory containing container_optimization components
- `containerization/` – Directory containing containerization components
- `cost_management/` – Directory containing cost_management components
- `crypto/` – Directory containing crypto components
- `dark/` – Directory containing dark components
- `data_curation/` – Directory containing data_curation components
- `data_lineage/` – Directory containing data_lineage components
- `data_visualization/` – Directory containing data_visualization components
- `database_management/` – Directory containing database_management components
- `defense/` – Directory containing defense components
- `demos/` – Directory containing demos components
- `dependency-graph.md` – Project file
- `dependency_injection/` – Directory containing dependency_injection components
- `deployment/` – Directory containing deployment components
- `distillation/` – Directory containing distillation components
- `distributed_training/` – Directory containing distributed_training components
- `docs_gen/` – Directory containing docs_gen components
- `documentation/` – Directory containing documentation components
- `documents/` – Directory containing documents components
- `dpo/` – Directory containing dpo components
- `edge_computing/` – Directory containing edge_computing components
- `email/` – Directory containing email components
- `embodiment/` – Directory containing embodiment components
- `encryption/` – Directory containing encryption components
- `environment_setup/` – Directory containing environment_setup components
- `eval_harness/` – Directory containing eval_harness components
- `events/` – Directory containing events components
- `evolutionary_ai/` – Directory containing evolutionary_ai components
- `examples/` – Directory containing examples components
- `exceptions/` – Directory containing exceptions components
- `feature_flags/` – Directory containing feature_flags components
- `feature_store/` – Directory containing feature_store components
- `file_system/` – Directory containing file_system components
- `finance/` – Directory containing finance components
- `formal_verification/` – Directory containing formal_verification components
- `fpf/` – Directory containing fpf components
- `git_analysis/` – Directory containing git_analysis components
- `git_operations/` – Directory containing git_operations components
- `graph_rag/` – Directory containing graph_rag components
- `ide/` – Directory containing ide components
- `identity/` – Directory containing identity components
- `image/` – Directory containing image components
- `interpretability/` – Directory containing interpretability components
- `llm/` – Directory containing llm components
- `logging_monitoring/` – Directory containing logging_monitoring components
- `logistics/` – Directory containing logistics components
- `logit_processor/` – Directory containing logit_processor components
- `lora/` – Directory containing lora components
- `maintenance/` – Directory containing maintenance components
- `market/` – Directory containing market components
- `matmul_kernel/` – Directory containing matmul_kernel components
- `meme/` – Directory containing meme components
- `ml_pipeline/` – Directory containing ml_pipeline components
- `model_context_protocol/` – Directory containing model_context_protocol components
- `model_merger/` – Directory containing model_merger components
- `model_ops/` – Directory containing model_ops components
- `module-reference.md` – Project file
- `module_template/` – Directory containing module_template components
- `multimodal/` – Directory containing multimodal components
- `nas/` – Directory containing nas components
- `networking/` – Directory containing networking components
- `networks/` – Directory containing networks components
- `neural/` – Directory containing neural components
- `ollama.md` – Project file
- `operating_system/` – Directory containing operating_system components
- `orchestrator/` – Directory containing orchestrator components
- `overview.md` – Project file
- `peft/` – Directory containing peft components
- `performance/` – Directory containing performance components
- `physical_management/` – Directory containing physical_management components
- `plugin_system/` – Directory containing plugin_system components
- `privacy/` – Directory containing privacy components
- `prompt_engineering/` – Directory containing prompt_engineering components
- `quantization/` – Directory containing quantization components
- `quantum/` – Directory containing quantum components
- `relations/` – Directory containing relations components
- `relationships.md` – Project file
- `release/` – Directory containing release components
- `rlhf/` – Directory containing rlhf components
- `scrape/` – Directory containing scrape components
- `search/` – Directory containing search components
- `security/` – Directory containing security components
- `semantic_router/` – Directory containing semantic_router components
- `serialization/` – Directory containing serialization components
- `simulation/` – Directory containing simulation components
- `skills/` – Directory containing skills components
- `slm/` – Directory containing slm components
- `softmax_opt/` – Directory containing softmax_opt components
- `soul/` – Directory containing soul components
- `spatial/` – Directory containing spatial components
- `ssm/` – Directory containing ssm components
- `static_analysis/` – Directory containing static_analysis components
- `synthetic_data/` – Directory containing synthetic_data components
- `system_discovery/` – Directory containing system_discovery components
- `telemetry/` – Directory containing telemetry components
- `templating/` – Directory containing templating components
- `terminal_interface/` – Directory containing terminal_interface components
- `testing/` – Directory containing testing components
- `tests/` – Directory containing tests components
- `text_to_sql/` – Directory containing text_to_sql components
- `tokenizer/` – Directory containing tokenizer components
- `tool_use/` – Directory containing tool_use components
- `tree_sitter/` – Directory containing tree_sitter components
- `utils/` – Directory containing utils components
- `validation/` – Directory containing validation components
- `vector_store/` – Directory containing vector_store components
- `video/` – Directory containing video components
- `wallet/` – Directory containing wallet components
- `website/` – Directory containing website components

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
- `dependency-graph.md`
- `module-reference.md`
- `ollama.md`
- `overview.md`
- `relationships.md`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [docs](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../README.md - Main project documentation
