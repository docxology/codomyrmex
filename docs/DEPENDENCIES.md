# Dependency Compatibility Guide

## Installation

```bash
# Core only (minimal)
uv sync

# Specific extra
uv sync --extra <group>

# Multiple extras
uv sync --extra audio --extra video --extra llm_providers

# All extras
uv sync --all-extras
```

## Optional Dependency Groups

| Group | Key packages | Notes |
|-------|-------------|-------|
| `scientific` | numpy, scipy, pandas | Required by many ML extras |
| `api` | fastapi, uvicorn, httpx | REST API server/client |
| `deployment` | fabric, ansible | Deployment automation |
| `code_review` | radon, pyscn | Cyclomatic complexity analysis |
| `language_models` | transformers, torch | HuggingFace model loading |
| `cloud` | boto3, google-cloud-*, azure-* | Cloud provider SDKs |
| `serialization` | msgpack, pyarrow, fastavro | Binary format support |
| `parsing` | tree-sitter, tree-sitter-languages | Syntax tree parsing |
| `modeling_3d` | trimesh, open3d | 3D geometry processing |
| `performance` | psutil, py-spy | Performance profiling |
| `observability` | opentelemetry-* | Distributed tracing |
| `physical_management` | pybullet | Physics simulation |
| `security_audit` | bandit | Security static analysis |
| `static_analysis` | radon, pylint, mypy | Code quality tools |
| `scrape` | firecrawl-py, playwright | Web scraping |
| `fpf` | feedparser, lxml | Feed parsing |
| `crypto` | cryptography, nacl | Cryptographic operations |
| `documents` | pypdf, python-docx, openpyxl | Document processing |
| `audio` | openai-whisper, pyttsx3, edge-tts | Speech processing |
| `video` | moviepy, opencv-python, Pillow | Video processing |
| `dark` | camelot-py, pdfplumber | PDF extraction |
| `formal_verification` | z3-solver | SAT/SMT solving |
| `obsidian` | watchdog | File system watching |
| `calendar` | google-api-python-client | Google Calendar |
| `email` | google-api-python-client, agentmail | Email providers |
| `llm_providers` | anthropic, openai, google-generativeai | LLM API clients |
| `embedding` | sentence-transformers | Text embeddings |
| `containerization` | docker | Docker SDK |
| `data_visualization` | matplotlib, plotly, dash | Chart generation |
| `cache` | redis | Redis backend |
| `soul` | soul-agent | Markdown-based LLM memory |
| `google_workspace` | google-api-python-client | Sheets, Docs, Drive |

## Known Conflicts

### aider — must NOT be installed as an extra

`aider-chat` conflicts with numpy/pyyaml version pins in this project's dependency tree
and is also incompatible with Python 3.13 (uses `audioop`, removed in 3.13).

**Correct installation:**
```bash
uv tool install aider-chat --python 3.12   # isolated tool, not project dep
```

Do NOT add `aider` to `pyproject.toml` optional dependencies.
The `aider` module at `src/codomyrmex/aider/` wraps it via subprocess.

### torch + cloud extras

Installing `language_models` (torch) together with cloud extras (boto3) can cause
version conflicts on some platforms. Prefer separate environments for ML training
vs. cloud orchestration workloads.

### audio on Python 3.13+

`openai-whisper` transitively requires `audioop` (stdlib, removed in 3.13).
Use Python 3.12 for the `audio` extra:
```bash
uv sync --extra audio --python 3.12
```

### modeling_3d + scientific

`open3d` pins `numpy<2.0`. Installing with `scientific` (numpy>=2.0) will conflict.
Install separately: `uv sync --extra modeling_3d` without `scientific`.

## Recommended Combinations

```bash
# AI development workstation
uv sync --extra llm_providers --extra language_models --extra scientific --extra api

# DevOps / CI agent
uv sync --extra deployment --extra containerization --extra cloud --extra observability

# Code analysis and review
uv sync --extra static_analysis --extra code_review --extra parsing --extra security_audit

# Document processing pipeline
uv sync --extra documents --extra scrape --extra fpf --extra dark
```

## CI Validation

The most common extras are validated in `.github/workflows/ci.yml`. When adding a new
optional dependency group, add a CI step that validates it installs cleanly:

```yaml
- name: Test extra install
  run: uv sync --extra <new-extra>
```
