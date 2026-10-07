"""Scoped advisory exceptions in ``scripts/security/audit_uv_lock.py``.

An exception must only apply while the lock pins the exact reviewed version;
any version change has to re-surface the advisory for a fresh review.
"""

from __future__ import annotations

import importlib.util
import sys

import pytest
from tests.support.repo_paths import REPO_ROOT


@pytest.fixture(scope="module")
def audit():
    script = REPO_ROOT / "scripts" / "security" / "audit_uv_lock.py"
    spec = importlib.util.spec_from_file_location("audit_uv_lock", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # dataclasses resolve annotations through sys.modules[cls.__module__].
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        yield module
    finally:
        sys.modules.pop(spec.name, None)


EXPORT = """\
anyio==4.14.2 \\
    --hash=sha256:abc
nltk==3.10.3 \\
    --hash=sha256:def
wasmtime==42.0.0 ; sys_platform != 'emscripten' \\
    --hash=sha256:ghi
"""


@pytest.mark.unit
def test_locked_version_parses_hashes_and_markers(audit) -> None:
    assert audit.locked_version(EXPORT, "nltk") == "3.10.3"
    assert audit.locked_version(EXPORT, "wasmtime") == "42.0.0"
    assert audit.locked_version(EXPORT, "WASMTIME") == "42.0.0"
    assert audit.locked_version(EXPORT, "missing") is None


@pytest.mark.unit
def test_locked_version_does_not_match_name_prefixes(audit) -> None:
    text = "nltk-extras==9.9.9 \\\n"
    assert audit.locked_version(text, "nltk") is None


@pytest.mark.unit
def test_ignores_apply_only_to_exact_reviewed_versions(audit) -> None:
    applied = {i.advisory for i in audit.applicable_ignores(EXPORT)}
    assert applied == {"PYSEC-2026-151", "PYSEC-2026-3740"}

    bumped = EXPORT.replace("nltk==3.10.3", "nltk==3.10.4")
    applied = {i.advisory for i in audit.applicable_ignores(bumped)}
    assert applied == {"PYSEC-2026-151"}


@pytest.mark.unit
def test_every_scoped_ignore_is_justified(audit) -> None:
    for ignore in audit.SCOPED_IGNORES:
        assert ignore.advisory
        assert ignore.package
        assert ignore.version.count(".") >= 1
        assert len(ignore.justification) > 40
