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


@pytest.mark.unit
def test_every_marker_specific_pin_is_retained(audit):
    text = (
        "numpy==2.4.6; python_version < '3.12'\n"
        "numpy==2.5.3; python_version >= '3.12'\n"
        "mlx==0.31.1; sys_platform == 'darwin'\n"
    )
    pairs = audit.locked_pairs(text)
    assert pairs == [("mlx", "0.31.1"), ("numpy", "2.4.6"), ("numpy", "2.5.3")]
    batches = audit.audit_batches(pairs)
    assert sorted(pair for batch in batches for pair in batch) == pairs
    assert all(len({name for name, _ in batch}) == len(batch) for batch in batches)


@pytest.mark.unit
def test_conflicting_pin_disables_global_exception(audit):
    conflicting = EXPORT + "wasmtime==43.0.0; sys_platform == 'darwin'\n"
    assert audit.locked_version(conflicting, "wasmtime") is None
    assert "PYSEC-2026-151" not in {
        item.advisory for item in audit.applicable_ignores(conflicting)
    }


@pytest.mark.unit
def test_advisory_exception_is_bound_to_report_version_and_retained(audit):
    vulnerability = {
        "id": "GHSA-example",
        "aliases": ["PYSEC-2026-151"],
        "fix_versions": [],
    }
    reviewed = {"name": "wasmtime", "version": "42.0.0", "vulns": [vulnerability]}
    unreviewed = {"name": "wasmtime", "version": "43.0.0", "vulns": [vulnerability]}
    audit.apply_scoped_ignores(reviewed)
    audit.apply_scoped_ignores(unreviewed)
    assert reviewed["vulns"] == []
    assert reviewed["ignored_vulns"][0]["id"] == "GHSA-example"
    assert reviewed["ignored_vulns"][0]["justification"]
    assert unreviewed["vulns"] == [vulnerability]
    assert "ignored_vulns" not in unreviewed


@pytest.mark.unit
@pytest.mark.parametrize(
    "text", ["", "package @ https://example.invalid/package.whl\n", "package>=1\n"]
)
def test_unauditable_export_fails_closed(audit, text):
    with pytest.raises(ValueError):
        audit.locked_pairs(text)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("dependency", "status"),
    [
        ({"name": "pkg", "version": "1", "vulns": []}, 1),
        ({"name": "pkg", "version": "1", "vulns": [{"id": "CVE-example"}]}, 0),
        (
            {"name": "pkg", "version": "1", "vulns": [{"aliases": ["PYSEC-2026-151"]}]},
            1,
        ),
        (
            {
                "name": "pkg",
                "version": "1",
                "vulns": [{"id": "CVE-example", "aliases": "bad"}],
            },
            1,
        ),
        (
            {
                "name": "pkg",
                "version": "1",
                "vulns": [],
                "skip_reason": "collection failed",
            },
            0,
        ),
    ],
)
def test_malformed_or_failed_collection_cannot_be_green(audit, dependency, status):
    with pytest.raises(ValueError):
        audit.validate_batch_report(
            {"dependencies": [dependency]}, [("pkg", "1")], status
        )


@pytest.mark.unit
def test_complete_report_must_cover_all_requested_versions(audit):
    dependency = {"name": "pkg", "version": "1", "vulns": []}
    assert audit.validate_batch_report(
        {"dependencies": [dependency]}, [("pkg", "1")], 0
    ) == [dependency]
    with pytest.raises(ValueError):
        audit.validate_batch_report(
            {"dependencies": [dependency]}, [("pkg", "1"), ("other", "2")], 0
        )
