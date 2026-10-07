"""Regression tests: each dashboard control is wired by exactly one script.

``assets/js/app.js`` is loaded on every page by ``templates/base.html``. It
used to bind the chat form, the test runner, the health refresh, the doc tree
and doc links, and the config editor, all of which the owning page template
also binds, so a single user action fired two handlers: two ``/api/docs`` or
``/api/config`` requests per click (the unencoded one could render the wrong
document), two config saves, a second ``/api/llm/config`` load and health
poller, and doc-tree folders that toggled twice per click (no-op).

The static checks read the real sources: app.js must not bind page-owned
elements or endpoints, and the owning template must still bind them. The
browser check renders the pages with the real Jinja environment used by
``WebsiteGenerator``, drives them in Chromium with every ``/api/*`` request
answered by canned JSON, and asserts one request per action. It runs only when
Node.js with the ``playwright`` package and its Chromium build is installed.

Zero-mock: no mocking; nothing is patched.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from codomyrmex.website.generator import WebsiteGenerator

HERE = Path(__file__).resolve().parent
WEBSITE_DIR = HERE.parents[2] / "src" / "codomyrmex" / "website"
TEMPLATES_DIR = WEBSITE_DIR / "templates"
APP_JS = WEBSITE_DIR / "assets" / "js" / "app.js"
HARNESS = HERE / "dashboard_request_counts.cjs"

_SCRIPT_RE = re.compile(r"<script\b([^>]*)>(.*?)</script>", re.DOTALL | re.IGNORECASE)
_LINE_COMMENT_RE = re.compile(r"^\s*//.*$", re.MULTILINE)
_Q = "['\"`]"

# Elements and endpoints that a page template wires itself; app.js must not.
PAGE_OWNED = {
    "chat.html": ["#chat-form", "#model-select", "/api/llm/config", "/api/chat"],
    "health.html": ["#run-tests-btn", "/api/tests", "/api/health"],
    "docs.html": [".doc-link", ".folder", "/api/docs/"],
    "config.html": [".config-file-link", "#save-config-btn", "/api/config"],
}
# Shared behaviour only app.js provides; no template may bind it again.
APP_OWNED = ["#refresh-data-btn", ".script-form", ".nav-link", "/api/execute"]


def _code(path: Path) -> str:
    """Return the JavaScript of *path* (inline scripts for a template)."""
    text = path.read_text(encoding="utf-8")
    if path.suffix != ".js":
        text = "\n".join(
            m.group(2)
            for m in _SCRIPT_RE.finditer(text)
            if not re.search(r"\bsrc\s*=", m.group(1))
        )
    return _LINE_COMMENT_RE.sub("", text)


def _binding_re(target: str) -> re.Pattern[str]:
    """Regex for code that looks up *target* (``#id``, ``.class``) or fetches it."""
    name = re.escape(target[1:])
    if target.startswith("#"):
        return re.compile(
            rf"getElementById\(\s*{_Q}{name}{_Q}\s*\)"
            rf"|querySelector(?:All)?\(\s*{_Q}[^'\"`]*#{name}(?![\w-])"
        )
    if target.startswith("."):
        return re.compile(
            rf"querySelector(?:All)?\(\s*{_Q}[^'\"`]*\.{name}(?![\w-])"
            rf"|getElementsByClassName\(\s*{_Q}{name}{_Q}"
        )
    return re.compile(rf"fetch\(\s*{_Q}{re.escape(target)}")


@pytest.mark.unit
@pytest.mark.parametrize(
    ("template", "target"),
    [(t, target) for t, targets in PAGE_OWNED.items() for target in targets],
)
def test_page_owned_controls_are_bound_only_by_their_template(template, target):
    pattern = _binding_re(target)
    assert pattern.search(_code(TEMPLATES_DIR / template)), (
        f"{template} no longer binds {target}; move the behaviour back into the "
        "template rather than into app.js"
    )
    assert not pattern.search(_code(APP_JS)), (
        f"app.js binds {target}, which {template} already wires: every action "
        "would fire twice"
    )


@pytest.mark.unit
@pytest.mark.parametrize("target", APP_OWNED)
def test_shared_controls_are_bound_only_by_app_js(target):
    pattern = _binding_re(target)
    assert pattern.search(_code(APP_JS)), f"app.js no longer binds {target}"
    for template in sorted(TEMPLATES_DIR.glob("*.html")):
        assert not pattern.search(_code(template)), (
            f"{template.name} binds {target}, which app.js already wires"
        )


@pytest.mark.unit
def test_app_js_does_not_shadow_page_functions():
    """A global declared in app.js replaces a template's same-named function."""
    app_globals = set(
        re.findall(r"^function\s+(\w+)", APP_JS.read_text("utf-8"), re.MULTILINE)
    )
    for template in sorted(TEMPLATES_DIR.glob("*.html")):
        page_functions = set(re.findall(r"\bfunction\s+(\w+)\s*\(", _code(template)))
        clash = app_globals & page_functions
        assert not clash, f"app.js redefines {sorted(clash)} from {template.name}"


@pytest.mark.unit
def test_binding_regex_matches_the_patterns_it_guards():
    """Guard against a vacuous pass of the static checks above."""
    samples = {
        "#chat-form": "document.getElementById('chat-form').addEventListener",
        ".doc-link": 'document.querySelectorAll(".doc-link").forEach',
        ".folder": "document.querySelectorAll('.doc-tree .folder')",
        "/api/docs/": "await fetch(`/api/docs/${path}`)",
    }
    for target, code in samples.items():
        assert _binding_re(target).search(code), target
    assert not _binding_re(".doc-link").search("querySelectorAll('.doc-links')")
    assert not _binding_re("#chat-form").search("getElementById('chat-form-x')")


# ---------------------------------------------------------------------------
# Real browser: one request per user action
# ---------------------------------------------------------------------------


def _node_env() -> dict[str, str] | None:
    """Environment in which ``require('playwright')`` and Chromium resolve."""
    node = shutil.which("node")
    if node is None:
        return None
    env = dict(os.environ)
    npm = shutil.which("npm")
    if npm is not None:
        try:
            root = subprocess.run(
                [npm, "root", "-g"], capture_output=True, text=True, timeout=30
            ).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            root = ""
        if root:
            env["NODE_PATH"] = os.pathsep.join(
                p for p in (env.get("NODE_PATH", ""), root) if p
            )
    probe = (
        "const fs = require('fs');"
        "const { chromium } = require('playwright');"
        "process.stdout.write(fs.existsSync(chromium.executablePath()) ? 'ok' : 'no');"
    )
    try:
        result = subprocess.run(
            [node, "-e", probe], capture_output=True, text=True, env=env, timeout=60
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return env if result.stdout == "ok" else None


NODE_ENV = _node_env()
requires_browser = pytest.mark.skipif(
    NODE_ENV is None, reason="Node.js playwright package with Chromium not installed"
)

SITE_CONTEXT = {
    "system": {"module_count": 2, "agent_count": 1, "environment": "test"},
    "modules": [{"name": "alpha"}, {"name": "beta"}],
    "scripts": [{"title": "Demo", "path": "demo/run.py", "description": "d"}],
    "config_files": [
        {"name": "pyproject.toml", "type": "toml"},
        {"name": "settings.yaml", "type": "yaml"},
    ],
    "doc_tree": {
        "children": [
            {
                "name": "guides",
                "children": [
                    {"name": "intro.md", "path": "guides/intro.md"},
                    # '#' and ' ' must be percent-encoded to reach the right doc.
                    {"name": "a b#c.md", "path": "guides/a b#c.md"},
                ],
            }
        ]
    },
    "health": {
        "uptime": "1h",
        "python": {"version": "3.12"},
        "modules": {
            "total": 2,
            "api_spec_pct": 50,
            "test_coverage_pct": 60,
            "mcp_spec_pct": 70,
        },
        "status_class": "ok",
        "status_text": "Healthy",
        "git": {
            "branch": "main",
            "commit_count": 10,
            "status": "clean",
            "dirty_files": 0,
            "last_commit": "abc initial",
        },
        "architecture_layers": [
            {"name": "Foundation", "color": "#fff", "modules": ["a", "b"]}
        ],
    },
    "awareness": {},
}
PAGES = [
    "index.html",
    "health.html",
    "scripts.html",
    "chat.html",
    "config.html",
    "docs.html",
]


@pytest.fixture(scope="module")
def browser_report(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("dashboard")
    generator = WebsiteGenerator(output_dir=str(tmp / "site"), root_dir=str(tmp))
    site = generator.output_dir
    site.mkdir()
    for page in PAGES:
        html = generator.env.get_template(page).render(**SITE_CONTEXT)
        (site / page).write_text(html, encoding="utf-8")
    shutil.copytree(generator.assets_dir, site / "assets")
    result = subprocess.run(
        ["node", str(HARNESS), str(site)],
        capture_output=True,
        text=True,
        env=NODE_ENV,
        timeout=240,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def _scenario(report: dict, name: str) -> dict:
    """Return one scenario's measurements, failing if the harness could not finish it."""
    scenario = report[name]
    assert "harnessError" not in scenario, f"{name}: {scenario['harnessError']}"
    return scenario


@requires_browser
@pytest.mark.unit
@pytest.mark.slow
def test_chat_sends_one_request_per_message(browser_report):
    chat = _scenario(browser_report, "chat")
    assert chat["llmConfigOnLoad"] == 1
    assert chat["chatPosts"] == 1
    assert chat["after"]["userMessages"] == 1
    assert chat["after"]["replies"] == 1
    assert chat["after"]["selectedModel"] == "m2"
    assert chat["whileSending"] == {
        "logBusy": "true",
        "buttonDisabled": True,
        "inputDisabled": True,
    }
    assert chat["after"]["logBusy"] is None
    assert chat["after"]["buttonDisabled"] is False
    assert "fade-in" in chat["after"]["replyClass"]
    assert chat["errors"] == []


@requires_browser
@pytest.mark.unit
@pytest.mark.slow
def test_health_starts_one_test_run_and_runs_one_poller(browser_report):
    health = _scenario(browser_report, "health")
    assert health["testPosts"] == 1
    assert health["statusPolls"] == 1
    assert health["buttonDisabledWhileRunning"] is True
    assert health["afterTests"] == {
        "output": "canned pytest output",
        "outputHidden": False,
        "buttonDisabled": False,
    }
    # One 5 s poller in 30 s of page time (app.js used to add a 30 s one).
    assert health["healthGetsPer30s"] == 6
    assert health["afterRefresh"] == {
        "uptime": "2h canned",
        "modules": "7",
        "status": "Healthy",
        "branch": "canned-branch",
        "commits": "42",
        "lastCommit": "def canned",
        "apiPct": "11%",
        "apiBarNow": "11",
        "connection": "Connected",
    }
    assert health["errors"] == []


@requires_browser
@pytest.mark.unit
@pytest.mark.slow
def test_docs_fetch_once_per_click_and_folders_toggle(browser_report):
    docs = _scenario(browser_report, "docs")
    assert docs["docGetsOnLoad"] == 1
    assert docs["docGetsPerClick"] == 1
    assert docs["docPathsRequested"] == ["/api/docs/guides/a b#c.md"]
    assert "Doc for guides/a b#c.md" in docs["docShown"]
    assert docs["clickedLinkWeight"] == "700"
    assert docs["folderInitial"] == {"expanded": "true", "display": ""}
    assert docs["folderAfterClick"] == {"expanded": "false", "display": "none"}
    assert docs["folderAfterEnter"] == {"expanded": "true", "display": ""}
    assert docs["errors"] == []


@requires_browser
@pytest.mark.unit
@pytest.mark.slow
def test_config_loads_and_saves_once_per_action(browser_report):
    config = _scenario(browser_report, "config")
    assert config["configGetsOnLoad"] == 1
    assert config["configGetsPerClick"] == 1
    assert config["afterLoad"] == {
        "label": "settings.yaml",
        "saveDisabled": False,
        "editorDisabled": False,
    }
    assert config["configPostsPerSave"] == 1
    assert config["savePathsRequested"] == ["POST /api/config"]
    assert config["afterSave"]["status"] == "✓ Saved"
    assert config["afterSave"]["saveDisabled"] is False
    assert config["errors"] == []


@requires_browser
@pytest.mark.unit
@pytest.mark.slow
def test_shared_app_js_behaviour_still_works(browser_report):
    scripts = _scenario(browser_report, "scripts")
    index = _scenario(browser_report, "index")
    assert scripts["executePosts"] == 1
    assert scripts["buttonLabel"] == "Run Script"
    assert scripts["errors"] == []
    assert index["refreshPosts"] == 1
    assert index["navCurrent"] == [True, "page"]
    assert index["altShortcutUrl"] == "/health.html"
    assert index["errors"] == []


@requires_browser
@pytest.mark.unit
@pytest.mark.slow
def test_non_json_replies_are_shown_as_errors(browser_report):
    broken = _scenario(browser_report, "nonJson")
    assert broken["chat"] == "Error: non-JSON response (HTTP 502)"
    assert broken["chatLogBusy"] is None
    assert broken["tests"] == "Server error: non-JSON response (HTTP 502)"
    # Regression: failed status polls were retried silently forever, leaving
    # "Run Tests" disabled. Five consecutive failures now end the wait.
    assert broken["lostRunner"].startswith("Lost contact with the test runner")
    assert "HTTP 502" in broken["lostRunner"]
    assert broken["lostRunnerButtonDisabled"] is False
    assert broken["lostRunnerPolls"] == 5
    assert broken["lostRunnerPollsLater"] == 5
    assert broken["connectionAfterOneFailure"] == "Connected"
    assert broken["connectionAfterTwoFailures"] == "Disconnected"
    assert broken["docs"] == "Error: Server error: non-JSON response (HTTP 502)"
    assert broken["config"] == "Error loading file: non-JSON response (HTTP 502)"
    assert broken["configSaveDisabled"] is True
