"""The repository's GitHub workflows must not splice untrusted text into shell.

Regression: ``trufflesecurity/trufflehog@v3.63.7`` expands
``${{ toJson(github.event.commits) }}`` inside a single-quoted bash string,
so on every push the commit messages became shell source. A message with an
apostrophe broke the Secret Detection job on main, and a crafted message in
a merged pull request could have run arbitrary commands in that job.
v3.97.4 passes only commit IDs, through an environment variable.

Attacker-controlled event fields (titles, bodies, messages, branch names)
belong in ``env:`` and must be read as quoted variables, never expanded
into ``run:`` or ``actions/github-script`` source.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

WORKFLOWS = Path(__file__).resolve().parents[3] / ".github" / "workflows"

# Event fields an outside contributor can set. Hashes, numbers and IDs are
# not free text and are allowed.
UNTRUSTED = re.compile(
    r"\$\{\{[^}]*?\b("
    r"github\.event\.(pull_request|issue|comment|review|review_comment|"
    r"head_commit|commits|discussion|discussion_comment|pages|workflow_run)"
    r"(\.[\w*]+)*"
    r"|github\.head_ref"
    r")[^}]*\}\}"
)
SAFE_SUFFIX = re.compile(r"\.(sha|number|id|before|after)\s*(\|\||\}\})")


def _steps():
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for job_name, job in (document.get("jobs") or {}).items():
            for index, step in enumerate(job.get("steps") or []):
                yield path.name, job_name, index, step


def _untrusted_expressions(text: str) -> list[str]:
    return [
        match.group(0)
        for match in UNTRUSTED.finditer(text)
        if not SAFE_SUFFIX.search(match.group(0))
    ]


@pytest.mark.unit
def test_workflows_are_found() -> None:
    assert len(list(_steps())) > 50


@pytest.mark.unit
def test_detector_flags_injection_and_allows_hashes() -> None:
    assert _untrusted_expressions("echo '${{ github.event.pull_request.title }}'")
    assert _untrusted_expressions("jq <<< '${{ toJson(github.event.commits) }}'")
    assert _untrusted_expressions('git checkout "${{ github.head_ref }}"')
    assert not _untrusted_expressions(
        "git diff ${{ github.event.pull_request.base.sha }}...HEAD"
    )


@pytest.mark.unit
def test_no_untrusted_event_text_in_run_or_script() -> None:
    offenders = []
    for workflow, job, index, step in _steps():
        sources = [step.get("run") or ""]
        with_args = step.get("with") or {}
        if isinstance(with_args, dict) and isinstance(with_args.get("script"), str):
            sources.append(with_args["script"])
        for source in sources:
            offenders.extend(
                f"{workflow}:{job}[{index}] {expr}"
                for expr in _untrusted_expressions(source)
            )
    assert not offenders, "move these into env: and quote them:\n" + "\n".join(
        offenders
    )


SHA_REF = re.compile(r"^[0-9a-f]{40}$")
TRUFFLEHOG_PIN = re.compile(
    r"trufflesecurity/trufflehog@(?P<ref>[^\s#]+)"
    r"(?:\s*#\s*\S*?@(?P<recorded>v?\d[\w.]*))?"
)


def _version(ref: str) -> tuple[int, ...]:
    return tuple(int(part) for part in ref.lstrip("v").split("."))


def _trufflehog_pins() -> list[tuple[str, str, str | None]]:
    """Every trufflehog pin, as (workflow, ref, recorded version).

    The ref is a version tag or a full commit SHA. A SHA records its version
    only in the trailing comment, and that comment has to be read from the raw
    file: ``_steps()`` parses YAML, which discards comments, so a SHA pin
    reaches the assertion with no version attached.
    """
    pins = []
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        for line in path.read_text(encoding="utf-8").splitlines():
            match = TRUFFLEHOG_PIN.search(line)
            if match:
                pins.append((path.name, match.group("ref"), match.group("recorded")))
    return pins


@pytest.mark.unit
def test_trufflehog_action_does_not_inline_commit_messages() -> None:
    pins = _trufflehog_pins()
    assert pins, "secret scanning step not found"
    for workflow, ref, recorded in pins:
        if SHA_REF.match(ref):
            assert recorded, (
                f"{workflow}: trufflehog@{ref} is pinned by SHA with no version "
                f"comment, so it cannot be compared against the 3.97.4 boundary "
                f"offline; pin by tag, or record the version in a comment"
            )
            version = recorded
        else:
            version = ref
        assert _version(version) >= (3, 97, 4), (
            f"{workflow}: trufflehog@{ref} (recorded {version}) expands commit "
            f"messages into its shell script"
        )
