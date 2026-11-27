<!-- readme: curated -->

# Codomyrmex

Codomyrmex is a modular Python workspace for software engineering and agent research. Developers can use individual utilities, while researchers can inspect the implementation and evidence behind the project's control-plane design. The [repository inventory](../docs/reference/inventory.md) explains how module, tool, and test counts are measured.

## Start with a local example

The [dependency-ordering walkthrough](../docs/verification/README.md) uses a fictional publishing checklist. Read the guide and its retained figure first. To reproduce the result locally, follow its sparse-checkout instructions. The replay uses Python, pytest, and Matplotlib 3.11.2, and checks that prerequisites come before dependent tasks and that a cycle is rejected. The example runs without service accounts or API keys.

For the broader Python package, the [root quick start](../README.md#-quick-start) uses Git, uv, and Python 3.11.5 or newer. It explains how to install the locked base environment and check the installed package version. The [setup guide](../docs/getting-started/setup.md) covers dependencies and configuration for individual features.

## Documentation and research

| If you want to… | Start here |
| --- | --- |
| Understand the project or choose a module | [Project overview](../README.md) and [documentation index](../docs/README.md) |
| Find a Python interface | [API reference](../docs/reference/api.md) and [modules](../src/codomyrmex/) |
| Read the research and its evidence limits | [Technical report source and build guide](../docs/manuscript/README.md) and [archived report edition](https://doi.org/10.5281/zenodo.21750801) |
| Contribute or report an issue | [Contributor guide](CONTRIBUTING.md), [issue templates](ISSUE_TEMPLATE/), and [PR template](PULL_REQUEST_TEMPLATE.md) |
| Inspect GitHub configuration or check status | [Workflow definitions](workflows/), [Actions](https://github.com/docxology/codomyrmex/actions), and [agent instructions](AGENTS.md) |

The technical report describes implementation contracts and controlled fixtures. External effectiveness and production safety remain open questions.

## Source, citation, and license

The implementation is in [`src/codomyrmex/`](../src/codomyrmex/). Use [CITATION.cff](../CITATION.cff) to cite the software, or the archived edition DOI above to cite the report. Codomyrmex is licensed under the [MIT License](../LICENSE).
