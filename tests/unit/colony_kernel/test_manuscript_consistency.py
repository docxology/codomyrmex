# SIZE_OK: This verifier intentionally keeps public claim surfaces together.

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest
import yaml
from tests.support.repo_paths import PACKAGE_ROOT, REPO_ROOT

from codomyrmex.colony_kernel.falsification_worker import AttackVector
from codomyrmex.colony_kernel.models import (
    AgentRole,
    AgentTrustProfile,
    FalsificationSeverity,
)
from codomyrmex.colony_kernel.role_adapter import RoleAdapter
from codomyrmex.manuscript.variables import _display_identifier

pytestmark = pytest.mark.unit

MANUSCRIPT_DIR = REPO_ROOT / "docs" / "manuscript"
FIGURE_GENERATORS_DIR = REPO_ROOT / "src" / "codomyrmex" / "manuscript" / "figures"
FIGURE_COMMON_PATH = "src/codomyrmex/manuscript/figures/_common.py"
FENCED_BLOCK_PATTERN = re.compile(r"```.*?```", re.DOTALL)

PUBLIC_CLAIM_FILES = [
    ".github/README.md",
    "CITATION.cff",
    "CLAUDE.md",
    "MODULES.md",
    "package.json",
    "skill.json",
    "CHANGELOG.md",
    "INDEX.md",
    "README.md",
    "docs/reference/inventory.md",
    "RELEASE_NOTES.md",
    "SECURITY.md",
    "SPEC.md",
    "PAI.md",
    "SKILL.md",
    "TODO.md",
    "src/README.md",
    "src/INDEX.md",
    "src/PAI.md",
    "src/SPEC.md",
    "src/codomyrmex/README.md",
    "src/codomyrmex/INDEX.md",
    "src/codomyrmex/SPEC.md",
    "src/codomyrmex/PAI.md",
    "docs/AGENTS.md",
    "docs/README.md",
    "docs/index.md",
    "docs/pai/architecture.md",
    "docs/todo/AGENTS.md",
    "docs/todo/COLONY_KERNEL.md",
    "docs/todo/README.md",
    "docs/manuscript/AGENTS.md",
    "docs/manuscript/README.md",
    "docs/manuscript/SYNTAX.md",
    "docs/manuscript/00_abstract.md",
    "docs/manuscript/00_00_cover.md",
    "docs/manuscript/01_introduction.md",
    "docs/manuscript/02_theory.md",
    "docs/manuscript/02_methodology.md",
    "docs/manuscript/03_results.md",
    "docs/manuscript/04_conclusion.md",
    "docs/manuscript/05_experimental_setup.md",
    "docs/manuscript/06_reproducibility.md",
    "docs/manuscript/07_scope_and_related_work.md",
    "docs/manuscript/08_active_inference.md",
    "docs/manuscript/09_research_roadmap.md",
    "docs/manuscript/10_formalism_code_crosswalk.md",
    "docs/manuscript/90_appendix_design_rationale.md",
    "docs/manuscript/manuscript.css",
    "docs/manuscript/preamble.md",
    "docs/manuscript/config.yaml",
    "docs/agi/emergence_and_scale.md",
    "docs/agi/recursive_self_improvement.md",
    "docs/agi/alignment_and_safety.md",
    "docs/agi/orchestration_as_cognition.md",
    "docs/agi/world_models.md",
    "docs/agi/scaffolding.md",
    "docs/agi/the_colony_thesis.md",
    "docs/agi/tool_use_and_agency.md",
    "docs/agi/memory_and_continuity.md",
    "docs/agi/formal_specification.md",
    "docs/agi/PAI.md",
    "docs/pai/on-ramp.md",
    "scripts/generate_manuscript_figures.py",
    FIGURE_COMMON_PATH,
    "config/colony_kernel/AGENTS.md",
    "config/colony_kernel/README.md",
    "config/colony_kernel/roles.yaml",
    "src/codomyrmex/colony_kernel/AGENTS.md",
    "src/codomyrmex/colony_kernel/API_SPECIFICATION.md",
    "src/codomyrmex/colony_kernel/MCP_TOOL_SPECIFICATION.md",
    "src/codomyrmex/colony_kernel/README.md",
    "src/codomyrmex/colony_kernel/SPEC.md",
    "src/codomyrmex/colony_kernel/PAI.md",
    "src/codomyrmex/model_context_protocol/PAI.md",
    "docs/modules/model_context_protocol/PAI.md",
    "docs/modules/colony_kernel/AGENTS.md",
    "docs/modules/colony_kernel/README.md",
    "docs/modules/colony_kernel/SPEC.md",
    "src/codomyrmex/documentation/docs/modules/colony_kernel/mcp_tool_specification.md",
    "docs/modules/agents/open_gauss/AGENTS.md",
    "docs/modules/agents/open_gauss/README.md",
    "docs/modules/agents/open_gauss/SPEC.md",
    "src/codomyrmex/documentation/docs/modules/colony_kernel/readme.md",
    "src/codomyrmex/skills/skills/custom/colony_kernel/decisions.md",
]

FORBIDDEN_CLAIMS = {
    re.compile(
        r"\bmultiplying four independent factors\b", re.IGNORECASE
    ): "the gate is weighted additive, not a product of factors",
    re.compile(
        r"\bmultiplicative structure\b", re.IGNORECASE
    ): "the gate is weighted additive, not multiplicative",
    re.compile(
        r"\bgate_score\s*=\s*base_score\b", re.IGNORECASE
    ): "falsification is not modeled as a base-score multiplier",
    re.compile(
        r"\bbase_score\b.{0,120}\bfalsification_penalty\b", re.IGNORECASE | re.DOTALL
    ): "falsification findings are handled through hard overrides and score components",
    re.compile(
        r"\bcannot be deceived\b", re.IGNORECASE
    ): "fresh-agent deception resistance must be softened, not absolute",
    re.compile(
        r"\bstructurally harder to deceive\b", re.IGNORECASE
    ): "deception resistance must be stated as a bounded measured effect",
    re.compile(
        r"\bno false passes\b", re.IGNORECASE
    ): "zero-mock tests reduce false-pass risk but do not prove impossibility",
    re.compile(
        r"\bmakes impossible\b", re.IGNORECASE
    ): "consequence memory increases difficulty; it is not an impossibility proof",
    re.compile(
        r"\bexperiment_results\.json\b"
    ): "the manuscript pipeline does not ship a raw experiment_results.json artifact",
    re.compile(
        r"\bcolony_analysis\.py\b"
    ): "the manuscript pipeline is z_generate_manuscript_variables.py plus compile_manuscript.py",
    re.compile(
        r"\btests/integration/seeds\.txt\b"
    ): "the kernel benchmark snapshot is deterministic and has no seed registry artifact",
    re.compile(
        r"\b5\s+(?:adversarial|attack)\s+vectors\b", re.IGNORECASE
    ): "the falsification worker has 10 vectors",
    re.compile(
        r"\bfive\s+(?:adversarial|attack)\s+vectors\b", re.IGNORECASE
    ): "the falsification worker has 10 vectors",
    re.compile(
        r"\b5\s+vectors\b", re.IGNORECASE
    ): "the falsification worker has 10 vectors",
    re.compile(
        r"\b[56]-check\b", re.IGNORECASE
    ): "the falsification worker has 10 adversarial checks",
    re.compile(
        r"\bmissing_rollback\b"
    ): "MCP falsification vectors should use canonical AttackVector values",
    re.compile(
        r"\bunderfunded_budget\b"
    ): "MCP falsification vectors should use canonical AttackVector values",
    re.compile(
        r"\bcircular_dependency\b"
    ): "MCP falsification vectors should use canonical AttackVector values",
    re.compile(
        r"\buntested_assumption\b"
    ): "MCP falsification vectors should use canonical AttackVector values",
    re.compile(
        r"\bblast_radius\b"
    ): "MCP falsification vectors should use canonical AttackVector values",
    re.compile(
        r"\bv1\.2\.7\b"
    ): "publication-facing entry points should advertise v1.3.0",
    re.compile(r'version:\s*"1\.2\.7"'): "YAML front matter should advertise v1.3.0",
    re.compile(r'"version"\s*:\s*"1\.0\.8"'): "package.json should advertise v1.3.0",
    re.compile(r'"version"\s*:\s*"1\.2\.7"'): "skill metadata should advertise v1.3.0",
    re.compile(
        r"\bPackage config \(version: 1\.2\.7\)", re.IGNORECASE
    ): "TODO hierarchy should advertise the current package version",
    re.compile(
        r"\*\*Version\*\*:\s*v1\.0\.0", re.IGNORECASE
    ): "colony-kernel source mirror docs should advertise v1.3.0",
    re.compile(
        r"\bwires five subsystems\b", re.IGNORECASE
    ): "the Colony Control Plane now documents eight subsystems",
    re.compile(
        r"\b129\s+top-level\s+modules?\b", re.IGNORECASE
    ): "publication-facing entry points should use the current 130-module inventory",
    re.compile(
        r"\b128\s+total\b", re.IGNORECASE
    ): "configuration diagrams should not preserve stale 128 totals",
    re.compile(
        r"\bmodule-specific\s+config\.yaml\s+files\b", re.IGNORECASE
    ): "configuration inventory should distinguish config dirs from config.yaml files",
    re.compile(
        r"\b35,183\b"
    ): "full-suite collection count must match the current inventory snapshot",
    re.compile(
        r"\b35,118\b"
    ): "full-suite collection count must match the current inventory snapshot",
    re.compile(
        r"\b35,137\b"
    ): "full-suite collection count must match the current inventory snapshot",
    re.compile(
        r"\b1,191\b"
    ): "docs inventory is currently 1,205 Markdown files under docs/",
    re.compile(
        r"\b1,192\b"
    ): "docs inventory is currently 1,205 Markdown files under docs/",
    re.compile(
        r"\b1,193\b"
    ): "docs inventory is currently 1,205 Markdown files under docs/",
    re.compile(
        r"\b1,194\b"
    ): "docs inventory is currently 1,205 Markdown files under docs/",
    re.compile(
        r"\b1,195\b"
    ): "docs inventory is currently 1,205 Markdown files under docs/",
    re.compile(
        r"\b35,122\b"
    ): "full-suite collection count must match the current inventory snapshot",
    re.compile(
        r"\b35,124\b"
    ): "full-suite collection count must match the current inventory snapshot",
    re.compile(r"35%2C124"): "full-suite collection badge is stale",
    re.compile(
        r"\b35,114\b"
    ): "full-suite collection count must match the current inventory snapshot",
    re.compile(
        r"\b34,451\b"
    ): "full-suite collection count must match the current inventory snapshot",
    re.compile(
        r"\b35,130\b"
    ): "full-suite collection is currently documented as 35,119 tests",
    re.compile(r"35%2C130"): "full-suite collection badge is stale",
    re.compile(
        r"\b35,131\b"
    ): "full-suite collection count must match the current inventory snapshot",
    re.compile(r"35%2C131"): "full-suite collection badge is stale",
    re.compile(r"35%2C137"): "full-suite collection badge is stale",
    re.compile(
        r"\b9\s+test\s+files\b", re.IGNORECASE
    ): "colony-kernel test suite currently spans 15 test files",
    re.compile(
        r"\bAll\s+52\s+tokens\b", re.IGNORECASE
    ): "manuscript variable inventory must be generated from the current token map",
    re.compile(
        r"\b456\s+tests\b", re.IGNORECASE
    ): "colony-kernel manuscript test count should come from the live scoped run",
    re.compile(
        r"\b457\s+tests\b", re.IGNORECASE
    ): "colony-kernel manuscript test count should come from the live scoped run",
    re.compile(
        r"\bscripts/03_render_pdf\.py\b"
    ): "manuscript rendering is handled by scripts/compile_manuscript.py",
    re.compile(
        r"\bprojects/codomyrmex/"
    ): "this repository is the project root; public commands should use root-relative paths",
    re.compile(
        r"\binfrastructure/rendering/pdf_renderer\.py\b"
    ): "local manuscript rendering is handled by scripts/compile_manuscript.py",
    re.compile(
        r"\bno figure or statistic can drift\b", re.IGNORECASE
    ): "artifact-backed claims reduce drift but should not overclaim impossibility",
    re.compile(
        r"\bplaceholder_version\b", re.IGNORECASE
    ): "publication metadata should not ship placeholder Zenodo DOI or record IDs",
    re.compile(
        r"\bdocumentation\s+&&\s+npm\s+run\b"
    ): "root package scripts should point at the live MkDocs surface",
    re.compile(
        r"\bcurrently\s+\*\*433\*\*", re.IGNORECASE
    ): "colony-kernel manuscript test count should come from the live scoped run",
    re.compile(
        r"\b33\s+tools?\b", re.IGNORECASE
    ): "active MCP documentation must use the measured profile counts",
    re.compile(
        r"~984\s+Total", re.IGNORECASE
    ): "active MCP documentation must use the measured profile counts",
    re.compile(
        r"tool_count:33", re.IGNORECASE
    ): "active MCP documentation must use the measured HTTP readonly count",
    re.compile(
        r"\b433\s+tests\b", re.IGNORECASE
    ): "colony-kernel manuscript test count should come from the live scoped run",
    re.compile(
        r"\b625\s+tests\b", re.IGNORECASE
    ): "colony-kernel manuscript test count is generated from the live scoped run",
    re.compile(
        r"\b633\s+tests\b", re.IGNORECASE
    ): "colony-kernel manuscript test count is generated from the live scoped run",
    re.compile(
        r"\b635\s+tests\b", re.IGNORECASE
    ): "colony-kernel manuscript test count is generated from the live scoped run",
    re.compile(
        r"\b636\s+tests\b", re.IGNORECASE
    ): "colony-kernel manuscript test count is generated from the live scoped run",
    re.compile(
        r"\b639\s+tests\b", re.IGNORECASE
    ): "colony-kernel manuscript test count is generated from the live scoped run",
    re.compile(
        r"\bagent retirement\b", re.IGNORECASE
    ): "role gating and module pruning should not be described as automatic agent retirement",
    re.compile(
        r"\bThree safety conditions\b", re.IGNORECASE
    ): "the gate has four hard overrides including critical falsification",
    re.compile(
        r"\bemergent property of the colony\b", re.IGNORECASE
    ): "the feedback loop is deterministic and explicitly sequenced",
    re.compile(
        r"\bemergent failure patterns\b", re.IGNORECASE
    ): "failure history should be described as accumulated signals, not emergent proof",
    re.compile(
        r"\btests/integration/test_falsification\.py\b"
    ): "the 10-vector worker is covered by the unit falsification suite",
    re.compile(
        r"\bscripts/analysis/(?:compare_conditions|analytical_gate_rate)\.py\b"
    ): "the manuscript does not ship those analysis scripts",
    re.compile(
        r"\bpower is sufficient\b", re.IGNORECASE
    ): "the configured protocol should not claim statistical power without raw traces",
    re.compile(
        r"\bheld-out workload\b", re.IGNORECASE
    ): "the configured protocol should not claim held-out validation without raw traces",
    re.compile(
        r"\bNo subsystem imports from another subsystem\b"
    ): "the current architecture uses standalone modules orchestrated by ColonyKernel",
    re.compile(
        r"\bno cross-subsystem imports\b", re.IGNORECASE
    ): "the current architecture uses explicit standalone modules and typed exchange",
    re.compile(
        r"\bcorrect and safe under\b", re.IGNORECASE
    ): "scope claims should say contract-tested, not generally safe",
    re.compile(
        r"\ball subsystem implementations\b", re.IGNORECASE
    ): "kernel.py is an integration/re-export surface, not the sole implementation file",
    re.compile(
        r"\bcomplete subsystem implementations\b", re.IGNORECASE
    ): "kernel.py is an integration/re-export surface, not the sole implementation file",
    re.compile(
        r"\btrust × pressure\b"
    ): "the gate is a weighted additive score with hard overrides",
    re.compile(
        r"\bchecked-in figures under `output/figures/`\b"
    ): "output/figures is a generated artifact directory",
    re.compile(
        r"\bempirical outcomes\b", re.IGNORECASE
    ): "results should be scoped as implementation outcomes unless raw traces are present",
    re.compile(
        r"\bHOLD outcome directs proposals to a falsification queue\b"
    ): "HOLD returns required evidence; callers may route through falsification",
    re.compile(
        r"\bconsumes falsification budget\b"
    ): "the manuscript should not claim a queue budget path absent a checked-in trace",
    re.compile(
        r"\b610 MCP tools\b", re.IGNORECASE
    ): "root docs must distinguish 608 runtime tools from 623 decorator lines",
    re.compile(
        r"\b610 decorators\b", re.IGNORECASE
    ): "production @mcp_tool decorator count is now 623, not 610",
    re.compile(
        r"\b92\.3%\s+branch\s+coverage\b", re.IGNORECASE
    ): "branch coverage must come from pytest --cov-branch, not statement coverage",
    re.compile(
        r"\b0\.65\s+promotion\s+threshold\b", re.IGNORECASE
    ): "kernel role promotion starts at trust >= 0.20 with >= 3 proposals",
    re.compile(
        r"\bpromotion\s+threshold\b.{0,80}\b0\.65\b", re.IGNORECASE | re.DOTALL
    ): "kernel role promotion starts at trust >= 0.20 with >= 3 proposals",
    re.compile(
        r"\bDISPATCHER\b.{0,80}\b0\.65\b", re.IGNORECASE | re.DOTALL
    ): "kernel DISPATCHER threshold is trust >= 0.50",
    re.compile(
        r"\bREPAIR_ANT\b.{0,80}\b0\.65\b", re.IGNORECASE | re.DOTALL
    ): "kernel REPAIR_ANT is not a 0.30-0.65 band",
    re.compile(
        r"\|\s*9\s*\|[^\n]*`REPAIR_ANT`", re.IGNORECASE
    ): "outcome 9 has trust >= 0.35 and should be MEMORY_ANT",
    re.compile(
        r"\|\s*12\s*\|[^\n]*`REPAIR_ANT`", re.IGNORECASE
    ): "outcome 12 has trust >= 0.50 and should be DISPATCHER",
}

REQUIRED_CLAIMS = {
    "docs/manuscript/03_results.md": [
        "{{FIGURE_CAPTION_GATE_SCORE_HEATMAP}}",
        "{{FIGURE_LABEL_GATE_SCORE_HEATMAP}}",
    ],
    "docs/manuscript/01_introduction.md": [
        "max(RISK, FAILURE)",
        "caller-reported outcomes",
    ],
    "docs/manuscript/00_abstract.md": [
        "measurably harder to pass",
        "failure memory raises friction",
        "stale or duplicate module locations",
    ],
    "docs/manuscript/02_methodology.md": [
        "standalone",
        "kernel",
        "HOLD",
        "REFUSE",
    ],
    "src/codomyrmex/colony_kernel/README.md": [
        "10 adversarial vectors",
    ],
    "docs/manuscript/05_experimental_setup.md": [
        "Proposed, not executed",
        "raw append-only traces",
    ],
    "docs/manuscript/04_conclusion.md": [
        "caller-supplied data",
        "Supported within one kernel process",
    ],
    "docs/manuscript/07_scope_and_related_work.md": [
        "Not a security boundary",
        "Not production- or scale-validated",
        "Not an integrated Active Inference implementation",
        "unattested report",
    ],
    "docs/manuscript/08_active_inference.md": [
        "deterministic and heuristic",
        "conceptual crosswalk",
    ],
    "docs/manuscript/09_research_roadmap.md": [
        "scoped research program",
        "{{RESULT_RESEARCH_ROADMAP_EVIDENCE_ROWS}}",
        "{{RESULT_RESEARCH_ROADMAP_DECISION_ROWS}}",
        "not a delivery timeline",
    ],
    "README.md": [
        "608 runtime MCP tools",
        "623 decorators",
        "1,207",
        "35,444",
    ],
}


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _read_figure_generators() -> str:
    """Concatenate figure module sources (split layout under ``figures/``)."""
    parts: list[str] = []
    for path in sorted(FIGURE_GENERATORS_DIR.glob("*.py")):
        if path.name in {"__init__.py", "generators.py"}:
            continue
        parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def _source_manuscript_files() -> list[Path]:
    return sorted(MANUSCRIPT_DIR.glob("[0-9][0-9]_*.md"))


def test_compiler_declares_scientific_narrative_order() -> None:
    """The rendered paper must not place the conclusion before methods/results."""
    import importlib.util

    compiler_path = REPO_ROOT / "scripts" / "compile_manuscript.py"
    spec = importlib.util.spec_from_file_location(
        "codomyrmex_compile_manuscript", compiler_path
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    names = [
        path.name
        for path in module._collect_sections(MANUSCRIPT_DIR, include_bookends=False)
    ]
    assert names.index("02_methodology.md") < names.index("05_experimental_setup.md")
    assert names.index("05_experimental_setup.md") < names.index("03_results.md")
    assert names.index("03_results.md") < names.index("04_conclusion.md")
    assert names.index("04_conclusion.md") < names.index("09_research_roadmap.md")
    assert names.index("09_research_roadmap.md") < names.index(
        "10_formalism_code_crosswalk.md"
    )
    assert names.index("10_formalism_code_crosswalk.md") < names.index(
        "90_appendix_design_rationale.md"
    )
    assert names[-1] == "99_references.md"


def _without_fenced_blocks(text: str) -> str:
    return FENCED_BLOCK_PATTERN.sub("", text)


def test_public_surfaces_do_not_carry_stale_reviewer_claims() -> None:
    failures: list[str] = []
    for rel_path in PUBLIC_CLAIM_FILES:
        path = REPO_ROOT / rel_path
        assert path.exists(), f"Expected public claim surface to exist: {rel_path}"
        text = path.read_text(encoding="utf-8")
        for pattern, reason in FORBIDDEN_CLAIMS.items():
            match = pattern.search(text)
            if match:
                snippet = " ".join(match.group(0).split())
                failures.append(f"{rel_path}: {snippet!r} - {reason}")

    assert not failures, "\n".join(failures)


def test_public_surfaces_include_corrected_claims() -> None:
    failures: list[str] = []
    for rel_path, snippets in REQUIRED_CLAIMS.items():
        text = _read(rel_path)
        for snippet in snippets:
            if snippet not in text:
                failures.append(f"{rel_path}: missing {snippet!r}")

    assert not failures, "\n".join(failures)


def test_manuscript_config_matches_kernel_contract() -> None:
    config = yaml.safe_load(_read("docs/manuscript/config.yaml"))
    experiment = config["experiment"]
    publication = config["publication"]

    assert config["paper"]["version"] == "1.3.0"
    assert config["paper"]["date"] == "auto"
    assert config["authors"][0]["orcid"] == "0000-0001-6232-9096"
    assert config["acknowledgements"] == [
        {
            "name": "Marek Pawel Bargiel",
            "contribution": "conceptual comments on pressure-aware gating / colony-control framing",
        }
    ]
    assert publication["doi"] == ""
    assert publication["doi_status"] == "forthcoming"
    assert publication["version_doi"] == ""
    assert publication["version_record"] == ""
    assert "placeholder" not in str(publication).lower()
    assert experiment["gate_score_weights"] == {
        "budget": 0.30,
        "risk": 0.30,
        "trust": 0.25,
        "completeness": 0.15,
    }
    assert experiment["trust_sandbox_score"] == 0.10
    assert experiment["trust_hard_floor"] == 0.30
    assert experiment["trust_promote_threshold"] == 0.20
    assert "configurable" in experiment["parameter_status_note"]
    assert "not empirically calibrated" in experiment["parameter_status_short"]
    assert experiment["falsification_vectors"] == len(AttackVector) == 10
    assert list(config["figures"]) == [
        "cover",
        "colony_pressure_loop",
        "pheromone_decay",
        "gate_score_heatmap",
        "trust_trajectory",
        "falsification_vectors",
        "subsystem_architecture",
        "gate_score_3d",
        "fep_correspondence",
        "research_roadmap",
        "formalism_code_crosswalk",
        "replay_contract",
        "attestation_event_chain",
        "safety_utility_frontier",
        "calibration_reliability",
        "persistence_recovery",
        "formalism_coverage",
        "research_status_matrix",
    ]
    assert (
        experiment["figure_parameters"]["score_min"]
        < experiment["figure_parameters"]["score_max"]
    )
    assert experiment["figure_parameters"]["decay_plot_points"] >= 2


def test_roles_yaml_matches_kernel_role_ladder_contract() -> None:
    roles = yaml.safe_load(_read("config/colony_kernel/roles.yaml"))
    thresholds = roles["thresholds"]

    assert thresholds["sandbox"]["max_trust"] == 0.30
    assert thresholds["repair_ant"] == {
        "min_trust": 0.20,
        "min_total_proposals": 3,
    }
    assert thresholds["memory_ant"] == {
        "min_trust": 0.35,
        "min_total_proposals": 3,
    }
    assert thresholds["dispatcher"] == {
        "min_trust": 0.50,
        "min_total_proposals": 3,
    }
    assert thresholds["guard_ant"] == {
        "min_trust": 0.70,
        "min_total_proposals": 3,
    }
    assert roles["defaults"] == {
        "new_agent_trust": 0.1,
        "new_agent_role": "sandbox",
    }


def test_source_publication_metadata_has_no_placeholders() -> None:
    source = yaml.safe_load(_read("docs/manuscript/config.yaml"))

    assert source["paper"]["date"] == "auto"
    assert source["authors"][0]["orcid"] == "0000-0001-6232-9096"
    assert source["publication"]["doi_status"] == "forthcoming"
    assert "placeholder" not in str(source["publication"]).lower()


def test_formalism_code_crosswalk_is_a_resolvable_evidence_contract() -> None:
    """Every crosswalk row must point to real code and evidence surfaces."""
    config = yaml.safe_load(_read("docs/manuscript/config.yaml"))
    entries = config["formalism_code_crosswalk"]
    assert entries
    assert {entry["status"] for entry in entries} >= {"implemented", "partial"}
    identifiers = [entry["id"] for entry in entries]
    assert len(identifiers) == len(set(identifiers))

    for entry in entries:
        assert entry["formal_object"]
        assert entry["bridge"]
        assert entry["claim_boundary"]
        for relative_path in [*entry["code_paths"], *entry["evidence_paths"]]:
            assert (REPO_ROOT / relative_path).exists(), relative_path


def test_implemented_roadmap_milestones_have_resolvable_artifacts() -> None:
    config = yaml.safe_load(_read("docs/manuscript/config.yaml"))
    implemented = [
        entry
        for entry in config["research_roadmap"]
        if entry.get("status") == "implemented"
    ]
    assert implemented
    for entry in implemented:
        paths = entry.get("artifact_paths")
        assert isinstance(paths, list) and paths, entry["id"]
        for relative_path in paths:
            assert (REPO_ROOT / relative_path).is_file(), relative_path


def test_manuscript_generator_uses_branch_coverage_contract() -> None:
    generator = _read("src/codomyrmex/manuscript/variables.py")

    assert "--cov-branch" in generator
    assert "percent_branches_covered" in generator


def test_variable_inventory_matches_syntax_and_source_tokens() -> None:
    generator = _read("src/codomyrmex/manuscript/variables.py")
    variable_block = generator.split("variables: dict[str, str] = {", 1)[1].split(
        "\n    return variables",
        1,
    )[0]
    generated_tokens = set(re.findall(r'"([A-Z0-9_]+)"\s*:', variable_block))
    source_tokens: set[str] = set()
    for manuscript_file in (REPO_ROOT / "docs" / "manuscript").glob("[0-9][0-9]_*.md"):
        source_tokens.update(
            re.findall(
                r"\{\{([A-Z0-9_]+)\}\}", manuscript_file.read_text(encoding="utf-8")
            )
        )

    figure_config = yaml.safe_load(_read("docs/manuscript/config.yaml"))["figures"]
    for key in figure_config:
        slug = re.sub(r"[^A-Z0-9]+", "_", key.upper()).strip("_")
        generated_tokens.update(
            {
                f"FIGURE_FILENAME_{slug}",
                f"FIGURE_LABEL_{slug}",
                f"FIGURE_WIDTH_{slug}",
                f"FIGURE_EVIDENCE_{slug}",
                f"FIGURE_CAPTION_{slug}",
            }
        )

    assert source_tokens <= generated_tokens
    assert {
        "CONFIG_ACKNOWLEDGEMENTS",
        "CONFIG_PARAMETER_STATUS_NOTE",
        "CONFIG_COVERAGE_FLOOR",
        "RESULT_PAIRED_LOCALITY_ROWS",
        "RESULT_TRUST_TRAJECTORY_ROWS",
        "RESULT_DECAY_ROWS",
        "RESULT_REPRESENTATIVE_GATE_ROWS",
        "RESULT_RESEARCH_ROADMAP_EVIDENCE_ROWS",
        "RESULT_RESEARCH_ROADMAP_DECISION_ROWS",
        "CONFIG_FORMALISM_CROSSWALK_COUNT",
        "RESULT_FORMALISM_CROSSWALK_ROWS",
        "RESULT_FORMALISM_CROSSWALK_EVIDENCE_ROWS",
        "RESULT_FORMAL_CROSSWALK_RESEARCH",
    } <= source_tokens
    assert "CONFIG_FORMALISM_CODE_CROSSWALK" in generated_tokens
    assert "RESULT_GATE_SCORE_PROMOTED" not in generated_tokens | source_tokens


def test_figure_metadata_is_single_source_for_embedded_captions() -> None:
    config = yaml.safe_load(_read("docs/manuscript/config.yaml"))
    figure_config = config["figures"]
    body = "\n".join(
        path.read_text(encoding="utf-8") for path in _source_manuscript_files()
    )
    for key, spec in figure_config.items():
        slug = re.sub(r"[^A-Z0-9]+", "_", key.upper()).strip("_")
        if key == "cover":
            continue
        for token in (
            f"{{{{FIGURE_CAPTION_{slug}}}}}",
            f"{{{{FIGURE_FILENAME_{slug}}}}}",
            f"{{{{FIGURE_LABEL_{slug}}}}}",
            f"{{{{FIGURE_WIDTH_{slug}}}}}",
        ):
            assert token in body, f"Missing configured figure token {token}"
        assert spec["caption"] not in body


def test_analytic_figure_captions_qualify_parameter_status() -> None:
    """Analytical and fixture figures must disclose their provisional inputs."""
    config = yaml.safe_load(_read("docs/manuscript/config.yaml"))
    for key in (
        "pheromone_decay",
        "gate_score_heatmap",
        "trust_trajectory",
        "gate_score_3d",
    ):
        caption = config["figures"][key]["caption"]
        assert "{{CONFIG_PARAMETER_STATUS_SHORT}}" in caption, key


def test_acknowledgements_are_tokenized_and_ordered_before_references() -> None:
    acknowledgement = _read("docs/manuscript/98_acknowledgements.md")
    assert acknowledgement == (
        "# Acknowledgements {#sec:acknowledgements .unnumbered}\n\n"
        "{{CONFIG_ACKNOWLEDGEMENTS}}\n"
    )
    compiler = _read("scripts/compile_manuscript.py")
    order = compiler.split("MANUSCRIPT_SECTION_ORDER = (", 1)[1].split(")", 1)[0]
    assert order.index('"98_acknowledgements.md"') < order.index('"99_references.md"')


def test_numbered_manuscript_has_no_raw_mutable_policy_literals() -> None:
    mutable_literal = re.compile(
        r"(?<![A-Za-z0-9_])(?:0\.(?:02|04|05|08|1(?:0)?|15|2(?:0|5)?|"
        r"3(?:0|5)?|5(?:0)?|6(?:0|5)?|7(?:0|5)?|85|9(?:0)?)|"
        r"[236]\.0|10\.0|20\b|30\b|200\b)"
    )
    failures: list[str] = []
    for path in _source_manuscript_files():
        if path.name == "00_00_cover.md":
            continue
        for match in mutable_literal.finditer(_without_fenced_blocks(path.read_text())):
            failures.append(f"{path.name}: raw mutable value {match.group(0)!r}")
    assert not failures, "\n".join(failures)


def test_falsification_figure_uses_canonical_attack_vector_names_and_severity() -> None:
    figures = _read_figure_generators()
    from codomyrmex.colony_kernel.falsification.models import _SEVERITY_RANK
    from codomyrmex.manuscript.variables import _falsification_vector_severities

    # Use the live source derivation here so manuscript generation can run its
    # scoped suite before replacing a stale snapshot. Figure rendering itself is
    # tested separately and fails closed when that snapshot is stale or missing.
    actual = _falsification_vector_severities(
        REPO_ROOT,
        AttackVector,
        _SEVERITY_RANK,
    )
    assert set(actual) == {vector.name for vector in AttackVector}
    assert set(actual.values()) <= {severity.name for severity in FalsificationSeverity}
    assert "SECURITY_RISK" in actual
    assert actual["SECURITY_RISK"] == "HIGH"
    assert "AttackVector" in figures
    assert "_falsification_severity_map" in figures
    assert "CIRCULAR_DEPS" not in figures


def test_manuscript_figure_generator_uses_live_snapshot_and_provenance() -> None:
    figures = _read_figure_generators()

    for required in (
        "VARIABLES_PATH",
        "CONFIG_PATH",
        "json.loads",
        "yaml.safe_load",
        "_figure_metadata",
        '"caption"',
        "CONFIG_BASE_EVAPORATION_RATE",
        "CONFIG_GATE_WEIGHT_",
        '_gate_weight("budget"',
        "CONFIG_TRUST_DELTA_PASS",
        "CONFIG_HASH",
        "REPRO_KERNEL_SOURCE_HASH",
        "GENERATION_TIMESTAMP",
        "_figure_provenance",
        "_add_provenance_note",
    ):
        assert required in figures

    for figure_name in (
        "cover.png",
        "colony_pressure_loop.png",
        "pheromone_decay.png",
        "gate_score_heatmap.png",
        "trust_trajectory.png",
        "falsification_vectors.png",
        "subsystem_architecture.png",
        "research_roadmap.png",
        "formalism_code_crosswalk.png",
    ):
        assert f'_save(fig, "{figure_name}")' in figures

    assert figures.count("_add_provenance_note(fig") >= 6


def test_mcp_falsification_specs_use_canonical_attack_vector_enum() -> None:
    canonical = {vector.value for vector in AttackVector}
    old_aliases = {
        "missing_rollback",
        "underfunded_budget",
        "circular_dependency",
        "untested_assumption",
        "blast_radius",
    }
    for rel_path in (
        "src/codomyrmex/colony_kernel/MCP_TOOL_SPECIFICATION.md",
        "src/codomyrmex/documentation/docs/modules/colony_kernel/mcp_tool_specification.md",
    ):
        text = _read(rel_path)
        for value in canonical:
            assert value in text, f"{rel_path} missing {value}"
        for alias in old_aliases:
            assert alias not in text, f"{rel_path} preserves old alias {alias}"


def test_compile_manuscript_accepts_digit_tokens_and_generated_metadata() -> None:
    import importlib.util

    module_path = REPO_ROOT / "scripts" / "compile_manuscript.py"
    spec = importlib.util.spec_from_file_location(
        "codomyrmex_compile_manuscript", module_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.TOKEN_PATTERN.findall(
        "{{RESULT_TRUST_AT_0}} {{CONFIG_TRIAL_COUNT_MINUS_1}}"
    ) == ["{{RESULT_TRUST_AT_0}}", "{{CONFIG_TRIAL_COUNT_MINUS_1}}"]
    args = module._build_pandoc_metadata_args(
        {
            "CONFIG_TITLE": "Generated title",
            "CONFIG_FIRST_AUTHOR": "Generated author",
            "CONFIG_PUBLICATION_DATE": "2099-01-01",
        },
        REPO_ROOT,
    )
    assert "date=2099-01-01" in args


def test_cover_page_metadata_and_red_link_contract() -> None:
    cover = _read("docs/manuscript/00_00_cover.md")
    preamble = _read("docs/manuscript/preamble.md")
    css = _read("docs/manuscript/manuscript.css")
    compiler = _read("scripts/compile_manuscript.py")

    for required in (
        "figures/cover.png",
        "{{CONFIG_TITLE}}",
        "{{CONFIG_SUBTITLE}}",
        "{{CONFIG_FIRST_AUTHOR}}",
        "{{CONFIG_PUBLICATION_DATE_DISPLAY}}",
        "{{CONFIG_AUTHOR_ORCID}}",
        "{{CONFIG_DOI}}",
    ):
        assert required in cover

    assert "allcolors=red" in preamble
    assert "color: #c1121f" in css
    assert "--css" in compiler
    assert "manuscript.css" in compiler
    assert "linkcolor=red" in compiler
    assert "urlcolor=red" in compiler
    assert "citecolor=red" in compiler


def test_manuscript_compiler_requires_crossref_toc_and_linked_render_contract() -> None:
    compiler = _read("scripts/compile_manuscript.py")

    for required in (
        "pandoc-crossref",
        "--number-sections",
        "link-citations=true",
        "linkReferences=true",
        "--mathml",
        "00_01_contents.md",
        "tableofcontents",
        'nav id="TOC"',
    ):
        assert required in compiler

    assert "cross-references will be unresolved" not in compiler
    assert 'shutil.which("pandoc-crossref")' not in compiler


def test_rendered_references_section_is_bibliography_anchor_only() -> None:
    references = _read("docs/manuscript/99_references.md")
    related_work = _read("docs/manuscript/07_scope_and_related_work.md")
    bibliography = _read("docs/manuscript/references.bib")

    assert "{#refs}" in references
    assert "[@key]" not in references
    assert "@fig:" not in references
    assert "citation key inventory" not in references.lower()
    assert "natbib" not in references.lower()

    cited = set(re.findall(r"@([A-Za-z][A-Za-z0-9_:-]+)", related_work))
    cited = {
        key for key in cited if not key.startswith(("sec:", "fig:", "tbl:", "eq:"))
    }
    defined = set(re.findall(r"^@[A-Za-z]+\{([^,]+),", bibliography, re.MULTILINE))
    assert cited <= defined, (
        f"Undefined related-work citations: {sorted(cited - defined)}"
    )
    assert {
        "yang2024swebench",
        "grasse1959reconstruction",
        "marsh1994trust",
        "nist2020zerotrust",
        "debenedetti2024agentdojo",
        "seto1998simplex",
        "friston2017active",
    } <= cited


def test_introduction_cites_control_plane_scholarship() -> None:
    introduction = _read("docs/manuscript/01_introduction.md")
    bibliography = _read("docs/manuscript/references.bib")

    cited = set(re.findall(r"@([A-Za-z][A-Za-z0-9_:-]+)", introduction))
    cited = {
        key for key in cited if not key.startswith(("sec:", "fig:", "tbl:", "eq:"))
    }
    defined = set(re.findall(r"^@[A-Za-z]+\{([^,]+),", bibliography, re.MULTILINE))
    assert cited <= defined, (
        f"Undefined introduction citations: {sorted(cited - defined)}"
    )
    assert {
        "wooldridge1995intelligent",
        "yang2024swebench",
        "grasse1959reconstruction",
        "marsh1994trust",
        "debenedetti2024agentdojo",
        "nist2020zerotrust",
        "peng2011reproducible",
    } <= cited


def test_introduction_token_inventory_is_documented() -> None:
    introduction = _read("docs/manuscript/01_introduction.md")
    generator = _read("src/codomyrmex/manuscript/variables.py")

    intro_tokens = set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", introduction))
    assert intro_tokens
    generated_tokens = set(
        re.findall(r'^\s+"([A-Z0-9_]+)"\s*:', generator, re.MULTILINE)
    )
    assert intro_tokens <= generated_tokens


def test_manuscript_source_uses_generated_cross_references() -> None:
    hardcoded_patterns = {
        re.compile(r"\bSection\s+\d+(?:\.\d+)*\b", re.IGNORECASE): "section",
        re.compile(r"\bTable\s+\d+(?:\.\d+)*\b", re.IGNORECASE): "table",
        re.compile(r"\bFigure\s+\d+(?:\.\d+)*\b", re.IGNORECASE): "figure",
        re.compile(r"\bEquation\s+\d+(?:\.\d+)*\b", re.IGNORECASE): "equation",
        re.compile(r"§\s*\d+(?:\.\d+)*"): "section-symbol",
        re.compile(r"\b(?:sec|fig|tbl|eq)\.\s*\d+", re.IGNORECASE): "abbrev",
    }
    failures: list[str] = []

    for path in _source_manuscript_files():
        text = _without_fenced_blocks(path.read_text(encoding="utf-8"))
        for pattern, kind in hardcoded_patterns.items():
            for match in pattern.finditer(text):
                failures.append(
                    f"{path.relative_to(REPO_ROOT)}: hardcoded {kind} reference {match.group(0)!r}"
                )

    assert not failures, "\n".join(failures)


def test_manuscript_tables_and_formalisms_have_crossref_labels() -> None:
    failures: list[str] = []
    equation_pattern = re.compile(
        r"\$\$(.*?)\$\$(?:\s*\{#(?P<label>eq:[^} ]+)[^}]*\})?", re.DOTALL
    )

    for path in _source_manuscript_files():
        lines = path.read_text(encoding="utf-8").splitlines()
        index = 0
        while index < len(lines):
            line = lines[index]
            next_line = lines[index + 1] if index + 1 < len(lines) else ""
            is_table = line.startswith("|") and re.match(r"^\|\s*:?-{3,}", next_line)
            if not is_table:
                index += 1
                continue

            while index < len(lines) and lines[index].startswith("|"):
                index += 1
            if index < len(lines) and re.fullmatch(
                r"\{\{RESULT_[A-Z0-9_]+_ROWS\}\}", lines[index].strip()
            ):
                index += 1
            while index < len(lines) and not lines[index].strip():
                index += 1
            caption = lines[index].strip() if index < len(lines) else ""
            if not caption.startswith(":") or "{#tbl:" not in caption:
                failures.append(
                    f"{path.relative_to(REPO_ROOT)}: markdown table missing Pandoc caption label"
                )
            index += 1

        text = _without_fenced_blocks(path.read_text(encoding="utf-8"))
        for match in equation_pattern.finditer(text):
            if match.group("label") is None:
                failures.append(
                    f"{path.relative_to(REPO_ROOT)}: display equation missing {{#eq:*}} label"
                )

    assert not failures, "\n".join(failures)


def test_crossref_labels_are_unique_referenced_and_resolved() -> None:
    label_counts: dict[str, int] = {}
    references: set[str] = set()

    for path in _source_manuscript_files():
        text = _without_fenced_blocks(path.read_text(encoding="utf-8"))
        for label in re.findall(r"\{#((?:fig|tbl|eq|sec):[A-Za-z0-9_.:-]+)\b", text):
            label_counts[label] = label_counts.get(label, 0) + 1
        references.update(re.findall(r"@((?:fig|tbl|eq|sec):[A-Za-z0-9_.:-]+)", text))

    config = yaml.safe_load(_read("docs/manuscript/config.yaml"))
    for key, spec in config["figures"].items():
        if key == "cover":
            continue
        slug = re.sub(r"[^A-Z0-9]+", "_", key.upper()).strip("_")
        token = f"{{{{FIGURE_LABEL_{slug}}}}}"
        if token in "\n".join(
            path.read_text(encoding="utf-8") for path in _source_manuscript_files()
        ):
            label = str(spec["label"])
            label_counts[label] = label_counts.get(label, 0) + 1

    duplicated = sorted(label for label, count in label_counts.items() if count > 1)
    unresolved = sorted(
        reference for reference in references if reference not in label_counts
    )
    # Figures and tables must be called out in prose. Display equations may be
    # numbered for stable review anchors without forcing a redundant sentence.
    unreferenced = sorted(
        label
        for label in label_counts
        if label.startswith(("fig:", "tbl:")) and label not in references
    )
    assert not duplicated, f"Duplicate crossref labels: {duplicated}"
    assert not unresolved, f"Crossref references without labels: {unresolved}"
    assert not unreferenced, f"Crossref labels without prose references: {unreferenced}"


def test_rendered_html_contains_toc_linked_citations_crossrefs_and_mathml() -> None:
    from bs4 import BeautifulSoup

    html_path = REPO_ROOT / "output" / "paper.html"
    if not html_path.exists():
        pytest.skip("rendered artifact is validated after the pipeline render stage")
    source_mtime = max(
        path.stat().st_mtime
        for path in [
            REPO_ROOT / "scripts" / "compile_manuscript.py",
            *_source_manuscript_files(),
        ]
    )
    if html_path.stat().st_mtime < source_mtime:
        pytest.skip(
            "Rendered HTML is older than manuscript sources; rerender before artifact check"
        )

    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    citation_links = soup.select("span.citation a[href^='#ref-'], a[href^='#ref-']")

    assert soup.find("nav", id="TOC") is not None
    assert citation_links
    assert soup.find(id="fig:architecture") is not None
    assert soup.find(id="tbl:quality_gates") is not None
    assert soup.find(id="eq:gate_score_detail") is not None
    assert soup.find("math") is not None


def test_public_inventory_counts_match_live_tree() -> None:
    import importlib.util

    inventory_path = REPO_ROOT / "scripts" / "doc_inventory.py"
    spec = importlib.util.spec_from_file_location(
        "codomyrmex_doc_inventory", inventory_path
    )
    assert spec is not None and spec.loader is not None
    inventory_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inventory_module)

    docs_count = inventory_module.count_documentation_markdown(REPO_ROOT)
    pytest_count = inventory_module.pytest_collect_count(REPO_ROOT)
    runtime_count = inventory_module.manifest_tool_count()
    readme = _read("README.md")
    inventory = _read("docs/reference/inventory.md")

    assert pytest_count is not None
    assert runtime_count is not None
    module_count = inventory_module.count_top_level_modules(REPO_ROOT)
    decorator_count = inventory_module.count_mcp_tool_decorators(REPO_ROOT)
    workflow_count = inventory_module.count_github_workflow_yml(REPO_ROOT)
    assert (
        f"**{module_count} top-level modules**" in readme
        or f"**{module_count}** top-level modules" in readme
    )
    assert f"**{decorator_count}** production `@mcp_tool`" in readme
    assert f"{docs_count:,} Markdown" in readme
    assert f"{docs_count:,} (`find docs" in inventory
    assert f"**{pytest_count:,}** collected tests" in readme
    assert f"| Pytest tests collected | {pytest_count:,}" in inventory
    assert f"{workflow_count} GitHub Actions workflows" in readme
    assert (
        f"| Runtime MCP tools | {runtime_count} (PAI merged manifest; standalone launcher full profile enumerates 605; HTTP defaults to 10 readonly tools) |"
        in inventory
    )
    assert f"| Production `@mcp_tool` decorators | {decorator_count} |" in inventory
    assert f"**{runtime_count}** runtime MCP tools" in readme
    assert f"{decorator_count} decorators" in readme

    # The MCP PAI guides are active operational contracts.  Keep their
    # profile/version claims tied to the measured inventory while leaving
    # historical release notes free to retain their original values.
    for rel_path in (
        "src/codomyrmex/model_context_protocol/PAI.md",
        "docs/modules/model_context_protocol/PAI.md",
    ):
        text = _read(rel_path)
        assert "608 PAI-manifest tools" in text
        assert "605 standalone full-profile tools" in text
        assert "10 readonly HTTP tools" in text
        assert "33 tools" not in text
        assert "~984 Total" not in text
        assert "tool_count:33" not in text
        assert "v1.1.9" not in text

    for rel_path in (
        "src/PAI.md",
        "src/SPEC.md",
        "src/codomyrmex/README.md",
        "src/codomyrmex/SPEC.md",
    ):
        text = _read(rel_path)
        assert "124 specialized modules" not in text
        assert "88 specialized modules" not in text
        assert "≥80%" not in text
        assert "inventory.md" in text
    for rel_path in ("src/PAI.md", "src/SPEC.md", "src/codomyrmex/SPEC.md"):
        assert "v1.1.9" not in _read(rel_path)
        assert "March 2026" not in _read(rel_path)


def test_todo_docs_reference_current_root_backlog_name() -> None:
    for rel_path in ("docs/todo/AGENTS.md", "docs/todo/README.md"):
        assert "TO-DO.md" not in _read(rel_path)
        assert "TODO.md" in _read(rel_path)


def test_manuscript_artifact_count_sources_match_documented_surfaces() -> None:
    import importlib.util

    module_path = REPO_ROOT / "src" / "codomyrmex" / "manuscript" / "variables.py"
    spec = importlib.util.spec_from_file_location(
        "codomyrmex_manuscript_variables", module_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module._count_colony_kernel_docs(REPO_ROOT) == 3
    expected_test_suites = len(
        list((REPO_ROOT / "tests" / "unit" / "colony_kernel").glob("test_*.py"))
    )
    assert module._count_colony_kernel_test_suites(REPO_ROOT) == expected_test_suites
    assert module._count_colony_kernel_config_files(REPO_ROOT) == 3
    assert (
        module._count_colony_kernel_mcp_tools(
            REPO_ROOT / "src" / "codomyrmex" / "colony_kernel"
        )
        == 8
    )


def test_root_package_scripts_point_to_live_documentation_surface() -> None:
    import json

    package_json = json.loads(_read("package.json"))
    scripts = package_json["scripts"]

    assert scripts["serve"] == "uv run python -m http.server 8000 --directory docs"
    assert scripts["start"] == "uv run python -m http.server 8000 --directory docs"
    assert scripts["build"] == (
        "uv run python src/codomyrmex/documentation/scripts/triple_check.py --repo-root . --fail-on-issues"
    )
    assert "mkdocs" not in " ".join(scripts.values())
    assert "documentation &&" not in " ".join(scripts.values())

    http_help = subprocess.run(
        ["uv", "run", "python", "-m", "http.server", "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert http_help.returncode == 0

    triple_check_help = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "src/codomyrmex/documentation/scripts/triple_check.py",
            "--help",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert triple_check_help.returncode == 0


@pytest.mark.parametrize(
    ("trust_score", "total_proposals", "expected_role"),
    [
        (1.0, 2, AgentRole.SANDBOX),
        (0.20, 3, AgentRole.REPAIR_ANT),
        (0.35, 3, AgentRole.MEMORY_ANT),
        (0.50, 3, AgentRole.DISPATCHER),
        (0.70, 3, AgentRole.GUARD_ANT),
    ],
)
def test_documented_kernel_role_ladder_matches_role_adapter(
    trust_score: float,
    total_proposals: int,
    expected_role: AgentRole,
) -> None:
    profile = AgentTrustProfile(
        agent_id="publication-contract-agent",
        role=AgentRole.SANDBOX,
        trust_score=trust_score,
        total_proposals=total_proposals,
    )

    assert RoleAdapter.infer_role(profile) == expected_role


_INFRASTRUCTURE_IMPORT_PATTERN = re.compile(
    r"^\s*(?:from infrastructure\b|import infrastructure\b)", re.MULTILINE
)


def test_infrastructure_import_pattern_detects_known_bad_case() -> None:
    """Proof-of-detection: the pattern used below must actually fire on a violation."""
    assert _INFRASTRUCTURE_IMPORT_PATTERN.search(
        "from infrastructure.config import Foo\n"
    )
    assert _INFRASTRUCTURE_IMPORT_PATTERN.search(
        "    import infrastructure.rendering\n"
    )
    assert not _INFRASTRUCTURE_IMPORT_PATTERN.search(
        "from codomyrmex.infrastructure_x import Foo\n"
    )
    assert not _INFRASTRUCTURE_IMPORT_PATTERN.search(
        "# import infrastructure.config for context\n"
    )


def test_layer_contract_forbids_infrastructure_imports() -> None:
    """docs/manuscript/layer_contract.yaml claims src/codomyrmex/ stays infrastructure-free
    outside its allowlist. This was previously documentation-only (consumed by no code
    anywhere in the repository) — this test makes the claim real."""
    contract = yaml.safe_load(_read("docs/manuscript/layer_contract.yaml"))
    allowed = {
        (REPO_ROOT / rel).resolve() for rel in contract["allow_infrastructure_imports"]
    }
    assert not allowed, "The manuscript layer contract has no infrastructure exceptions"

    violations: list[str] = []
    for path in sorted((REPO_ROOT / "src" / "codomyrmex").rglob("*.py")):
        if path.resolve() in allowed:
            continue
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if _INFRASTRUCTURE_IMPORT_PATTERN.search(text):
            violations.append(str(path.relative_to(REPO_ROOT)))

    assert not violations, (
        "src/codomyrmex/ files import infrastructure.* outside the layer_contract.yaml "
        f"allowlist: {violations}"
    )


def test_display_identifier_preserves_machine_value_for_rendered_line_breaks() -> None:
    """Rendered provenance may wrap hashes but must remain losslessly comparable."""
    raw = "0123456789abcdef" * 4
    displayed = _display_identifier(raw)

    assert displayed != raw
    assert " " in displayed
    assert displayed.replace(" ", "") == raw
    assert _display_identifier("not-a-digest") == "not-a-digest"
