# Documentation and Signposting Audit Report
Generated: comprehensive_audit.py
================================================================================
## Summary
**Total Issues Found**: 409

### Issue Breakdown
- **Examples Migration**: 43
- **Placeholders**: 366

## Placeholders Found
- **plugins/SPEC.md** (line 3): `Core Concept`
  - Content: `## Core Concept...`
- **src/template/AGENTS_ROOT_TEMPLATE.md** (line 25): `TODO`
  - Content: `- Record outcomes in shared telemetry and update TODO queues when necessary....`
- **src/template/AGENTS_TEMPLATE.md** (line 27): `TODO`
  - Content: `- Record outcomes in shared telemetry and update TODO queues when necessary....`
- **src/template/AGENTS.md** (line 29): `TODO`
  - Content: `- Record outcomes in shared telemetry and update TODO queues when necessary....`
- **src/codomyrmex/documentation/coverage_assessment.md** (line 81): `TODO`
  - Content: `1. **Placeholder Content**: 554 TODO/FIXME markers need completion...`
- **src/codomyrmex/documentation/USAGE_EXAMPLES.md** (line 5): `TODO`
  - Content: `<!-- TODO: Ensure all examples are tested and accurately reflect the script's ca...`
- **src/codomyrmex/tools/AGENTS.md** (line 36): `TODO`
  - Content: `- Record outcomes in shared telemetry and update TODO queues when necessary....`
- **src/codomyrmex/pattern_matching/MCP_TOOL_SPECIFICATION.md** (line 27): `TODO`
  - Content: `| `query`           | `string`      | Yes      | The literal string or regular e...`
- **src/codomyrmex/environment_setup/USAGE_EXAMPLES.md** (line 214): `example.com`
  - Content: `pip install git+https://example.com/vendor/special_xyz_python_lib.git#egg=specia...`
- **src/codomyrmex/plugin_system/README.md** (line 346): `example.com`
  - Content: `'integration_plugin': {'endpoint': 'https://api.example.com'}...`
- **src/codomyrmex/scrape/README.md** (line 69): `example.com`
  - Content: `result = scraper.scrape("https://example.com", options)...`
- **src/codomyrmex/scrape/README.md** (line 103): `example.com`
  - Content: `crawl_result = scraper.crawl("https://example.com", options)...`
- **src/codomyrmex/scrape/README.md** (line 122): `example.com`
  - Content: `map_result = scraper.map("https://example.com")...`
- **src/codomyrmex/scrape/README.md** (line 126): `example.com`
  - Content: `search_result = scraper.map("https://example.com", search="docs")...`
- **src/codomyrmex/scrape/README.md** (line 174): `example.com`
  - Content: `urls=["https://example.com/article"],...`
- **src/codomyrmex/scrape/README.md** (line 183): `example.com`
  - Content: `urls=["https://example.com/article"],...`
- **src/codomyrmex/scrape/README.md** (line 263): `example.com`
  - Content: `result = scraper.scrape("https://example.com")...`
- **src/codomyrmex/module_template/SPEC.md** (line 63): `TODO`
  - Content: `- **Documentation**: Generated docs must represent the "Ideal" state (no "Requir...`
- **src/codomyrmex/module_template/SPEC.md** (line 63): `Requirement 1`
  - Content: `- **Documentation**: Generated docs must represent the "Ideal" state (no "Requir...`
- **src/codomyrmex/api/README.md** (line 64): `example.com`
  - Content: `docs = generate_api_docs("My API", "1.0.0", base_url="https://api.example.com")...`
- **src/codomyrmex/fpf/FPF-Spec.md** (line 1): `Core Concept`
  - Content: `# First Principles Framework (FPF) — Core Conceptual Specification...`
- **src/codomyrmex/fpf/FPF-Spec.md** (line 12041): `TBD`
  - Content: `**DRR pointer:** **REQUIRED before Core admission.** `DRR‑SERV‑POLYSEMY‑<id>` (T...`
- **src/codomyrmex/fpf/FPF-Spec.md** (line 22086): `TBD`
  - Content: `**SoTA pack binding note.** If a SoTA Synthesis Pack exists for KD‑CAL reliabili...`
- **src/codomyrmex/fpf/FPF-Spec.md** (line 22199): `TBD`
  - Content: `* **F2 — Structured outline.** Template present; coherent sections; criteria mos...`
- **src/codomyrmex/fpf/FPF-Spec.md** (line 22244): `TBD`
  - Content: `**Inclusion criteria.** All expected sections exist; cross‑references are consis...`
- **src/codomyrmex/fpf/FPF-Spec.md** (line 22510): `TBD`
  - Content: `* **F2?** Template is complete; terms don’t drift; “TBD” acceptance is explicitl...`
- **src/codomyrmex/fpf/FPF-Spec.md** (line 22691): `Core Concept`
  - Content: `### C.3:6 - Core Concepts (informative summary; authoritative norms live in C.3....`
- **src/codomyrmex/fpf/FPF-Spec.md** (line 26296): `TBD`
  - Content: `* **MethodDescription.** “JTBD interviews + onboarding flow experiments.”...`
- **src/codomyrmex/fpf/FPF-Spec.md** (line 30789): `Core Concept`
  - Content: `*   **Core Concept:** The HF-Loop is a formal method of inquiry designed to dist...`
- **src/codomyrmex/fpf/FPF-Spec.md** (line 32963): `TODO`
  - Content: `| **CC‑MVPK‑4b (Lean assurance)** | If `AssuranceLane‑Lite` is used, presence bi...`

*... and 336 more placeholders*

## Examples Migration Issues
Found references to old `examples/` paths that should be updated to `scripts/examples/`:
- **config/AGENTS.md** (line 7):
  ```
  - [examples](examples/AGENTS.md)...
  ```
- **config/AGENTS.md** (line 154):
  ```
  - **Quick Start**: [examples/workflow-basic.json](examples/workflow-basic.json) - Basic configuratio...
  ```
- **config/AGENTS.md** (line 155):
  ```
  - **Docker Setup**: [examples/docker-compose.yml](examples/docker-compose.yml) - Container deploymen...
  ```
- **scripts/README.md** (line 24):
  ```
  - [examples](examples/README.md)...
  ```
- **scripts/README.md** (line 470):
  ```
  - **Examples**: [examples/README.md](examples/README.md)...
  ```
- **scripts/AGENTS.md** (line 25):
  ```
  - [examples](examples/AGENTS.md)...
  ```
- **src/codomyrmex/physical_management/docs/index.md** (line 18):
  ```
  - Explore the [Examples](../../../examples/physical_management/) directory for usage examples....
  ```
- **src/codomyrmex/physical_management/docs/index.md** (line 24):
  ```
  - [Examples](../../../examples/physical_management/) - Usage examples and demonstrations...
  ```
- **scripts/project_orchestration/README.md** (line 6):
  ```
  - [examples](examples/README.md)...
  ```
- **scripts/project_orchestration/AGENTS.md** (line 7):
  ```
  - [examples](examples/AGENTS.md)...
  ```
- **scripts/project_orchestration/AGENTS.md** (line 510):
  ```
  - **Comprehensive Demo**: [examples/comprehensive_workflow_demo.py](examples/comprehensive_workflow_...
  ```
- **scripts/fpf/README.md** (line 6):
  ```
  - [examples](../examples/README.md)...
  ```
- **scripts/fpf/AGENTS.md** (line 7):
  ```
  - [examples](../examples/AGENTS.md)...
  ```
- **docs/project/documentation-audit-report.md** (line 79):
  ```
  - [examples](examples/AGENTS.md)......
  ```
- **docs/project/documentation-audit-report.md** (line 83):
  ```
  - **Quick Start**: [examples/workflow-basic.json](examples/workflow-basic.json) - Basic configuratio...
  ```
- **docs/project/documentation-audit-report.md** (line 87):
  ```
  - **Docker Setup**: [examples/docker-compose.yml](examples/docker-compose.yml) - Container deploymen...
  ```
- **docs/project/documentation-audit-report.md** (line 91):
  ```
  - [examples](examples/README.md)......
  ```
- **docs/project/documentation-audit-report.md** (line 95):
  ```
  - **Examples**: [examples/README.md](examples/README.md)......
  ```
- **docs/project/documentation-audit-report.md** (line 99):
  ```
  - [examples](examples/AGENTS.md)......
  ```
- **docs/project/documentation-audit-report.md** (line 103):
  ```
  - Explore the [Examples](../../../examples/physical_management/) directory for usage examples.......
  ```
- **docs/project/documentation-audit-report.md** (line 107):
  ```
  - [Examples](../../../examples/physical_management/) - Usage examples and demonstrations......
  ```
- **docs/project/documentation-audit-report.md** (line 111):
  ```
  - [examples](examples/README.md)......
  ```
- **docs/project/documentation-audit-report.md** (line 115):
  ```
  - [examples](examples/AGENTS.md)......
  ```
- **docs/project/documentation-audit-report.md** (line 119):
  ```
  - **Comprehensive Demo**: [examples/comprehensive_workflow_demo.py](examples/comprehensive_workflow_...
  ```
- **docs/project/documentation-audit-report.md** (line 123):
  ```
  - [examples](../examples/README.md)......
  ```
- **docs/project/documentation-audit-report.md** (line 127):
  ```
  - [examples](../examples/AGENTS.md)......
  ```
- **docs/project/documentation-audit-report.md** (line 131):
  ```
  - [examples](examples/AGENTS.md).........
  ```
- **docs/project/documentation-audit-report.md** (line 135):
  ```
  - **Quick Start**: [examples/workflow-basic.json](examples/workflow-basic.json) - Basic configuratio...
  ```
- **docs/project/documentation-audit-report.md** (line 139):
  ```
  - **Docker Setup**: [examples/docker-compose.yml](examples/docker-compose.yml) - Container deploymen...
  ```
- **docs/project/documentation-audit-report.md** (line 143):
  ```
  - [examples](examples/README.md).........
  ```

*... and 13 more examples migration issues*

## Recommendations
1. Fix all broken links identified above
2. Remove duplicate content sections
3. Update examples migration references
4. Standardize AGENTS.md structure across all files
5. Add missing README.md and AGENTS.md files
6. Replace remaining placeholders with actual content

================================================================================