"""Check accessible names in the actual SPA markup and field renderer."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from html.parser import HTMLParser
from pathlib import Path

import pytest

SPA = (
    Path(__file__).resolve().parents[3] / "src/codomyrmex/pai_pm/server/spa/index.html"
)


class FormMarkup(HTMLParser):
    """Parse actual HTML fragments emitted by the SPA."""

    def __init__(self) -> None:
        super().__init__()
        self.controls: dict[str, dict[str, str | None]] = {}
        self.all_controls: list[dict[str, str | None]] = []
        self.labels: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "label" and attributes.get("for"):
            self.labels.add(str(attributes["for"]))
        if tag in {"input", "textarea", "select"} and attributes.get("id"):
            self.controls[str(attributes["id"])] = attributes
        if tag in {"input", "textarea", "select"}:
            self.all_controls.append(attributes)


def literal_markup() -> FormMarkup:
    """Parse HTML opening tags from the real JavaScript string literals."""
    parser = FormMarkup()
    source = SPA.read_text()
    for match in re.finditer(r"<(?:input|textarea|select|label)\b[^>]*>", source):
        # Only opening tags are needed; template interpolation never replaces
        # the static ID, explicit label association, or accessible name.
        fragment = FormMarkup()
        fragment.feed(match.group())
        parser.controls.update(fragment.controls)
        parser.all_controls.extend(fragment.all_controls)
        parser.labels.update(fragment.labels)
    return parser


@pytest.mark.parametrize(
    "control_id",
    [
        "data-search-input",
        "add-task-text",
        "add-task-priority",
        "add-task-spec",
        "add-task-depends",
        "gh-link-project",
        "gh-link-repo",
        "gh-sync-project",
        "gh-diff-project",
        "gh-new-issue-title",
        "gh-cleanup-repo",
        "interview-answer",
        "interview-entity",
        "interview-type",
        "cal-new-summary",
        "email-to",
        "email-subject",
        "email-body",
    ],
)
def test_unlabelled_controls_have_accessible_names(control_id: str) -> None:
    """Controls retain names after placeholders disappear during input."""
    markup = literal_markup()
    control = markup.controls[control_id]
    assert control.get("aria-label") or control_id in markup.labels


@pytest.mark.parametrize(
    "control_id",
    [
        "cal-new-date",
        "cal-new-time",
        "cal-new-duration",
        "cal-new-project",
        "cal-new-desc",
    ],
)
def test_calendar_visible_labels_name_controls(control_id: str) -> None:
    """Visible calendar labels have explicit associations and stay authoritative."""
    markup = literal_markup()
    assert control_id in markup.labels
    assert "aria-label" not in markup.controls[control_id]


def test_every_form_control_has_a_name() -> None:
    """Include inline editors and selectors without stable static IDs."""
    markup = literal_markup()
    for control in markup.all_controls:
        control_id = control.get("id", "") or ""
        if control_id.startswith("f-"):
            # field() composes these IDs; its real output is checked below.
            continue
        assert (
            control.get("aria-label")
            or control.get("title")
            or control_id in markup.labels
        ), control


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is unavailable")
def test_inline_javascript_parses() -> None:
    """The complete production inline scripts remain syntactically valid."""
    for script in re.findall(
        r"<script\b[^>]*>(.*?)</script>", SPA.read_text(), re.DOTALL
    ):
        subprocess.run(
            ["node", "--check"],
            input=script,
            text=True,
            capture_output=True,
            check=True,
        )


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is unavailable")
@pytest.mark.parametrize("kind", ["text", "textarea", "select"])
def test_field_renderer_keeps_visible_label(kind: str) -> None:
    """Execute the production renderer, including an empty placeholder."""
    source = SPA.read_text()
    renderer = source[source.index("    function field(") :]
    renderer = renderer[: renderer.index("\n    // ===")]
    escape = source[source.index("    function esc(") :].split("\n", 1)[0]
    script = (
        escape
        + renderer
        + "\nconsole.log(field('example', 'Visible name', "
        + json.dumps(kind)
        + ", '', '', ['Option']));"
    )
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=True
    )
    markup = FormMarkup()
    markup.feed(result.stdout)
    assert "f-example" in markup.labels
    assert "aria-label" not in markup.controls["f-example"]
