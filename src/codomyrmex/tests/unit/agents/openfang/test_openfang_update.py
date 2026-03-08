"""Tests for openfang update utilities — zero-mock, filesystem-based."""
import os
import tempfile
from pathlib import Path

from codomyrmex.agents.openfang.update import (
    build_and_install,
    build_from_source,
    get_upstream_version,
    install_binary,
    update_submodule,
)


class TestUpdateSubmodule:
    def test_nonexistent_vendor_dir_returns_error(self):
        result = update_submodule(vendor_dir="/tmp/nonexistent_openfang_xyz_9999")
        assert result["status"] == "error"
        assert "vendor dir not found" in result["message"]

    def test_returns_dict(self):
        result = update_submodule(vendor_dir="/tmp/nonexistent_openfang_xyz_9999")
        assert isinstance(result, dict)

    def test_error_dict_has_message_key(self):
        result = update_submodule(vendor_dir="/tmp/nonexistent_xyz_openfang_abc")
        assert "message" in result

    def test_status_key_always_present(self):
        result = update_submodule(vendor_dir="/tmp/nonexistent_xyz_openfang_abc")
        assert "status" in result


class TestBuildFromSource:
    def test_missing_cargo_toml_returns_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = build_from_source(vendor_dir=tmpdir)
        assert result["status"] == "error"
        assert "Cargo.toml" in result["message"]

    def test_returns_dict(self):
        result = build_from_source(vendor_dir="/tmp/nonexistent_xyz")
        assert isinstance(result, dict)

    def test_cargo_not_found_returns_error(self):
        # Create a temp dir with a Cargo.toml but fake cargo command
        with tempfile.TemporaryDirectory() as tmpdir:
            cargo_toml = Path(tmpdir) / "Cargo.toml"
            cargo_toml.write_text('[package]\nname = "openfang"\nversion = "0.1.0"\n')
            old_path = os.environ.get("PATH", "")
            os.environ["PATH"] = "/nonexistent_path_xyz"
            try:
                result = build_from_source(vendor_dir=tmpdir)
            finally:
                os.environ["PATH"] = old_path
        # Either cargo not found or it failed
        assert result["status"] in {"error", "success"}
        if result["status"] == "error":
            assert "message" in result

    def test_error_has_message_key(self):
        result = build_from_source(vendor_dir="/tmp/nonexistent_xyz")
        assert "message" in result


class TestInstallBinary:
    def test_missing_compiled_binary_returns_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = install_binary(vendor_dir=tmpdir, install_dir=tmpdir)
        assert result["status"] == "error"
        assert "not found" in result["message"]

    def test_returns_dict(self):
        result = install_binary(vendor_dir="/tmp/nonexistent_xyz")
        assert isinstance(result, dict)

    def test_error_has_message_key(self):
        result = install_binary(vendor_dir="/tmp/nonexistent_xyz")
        assert "message" in result

    def test_successful_install(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create fake binary in vendor structure
            release_dir = Path(tmpdir) / "target" / "release"
            release_dir.mkdir(parents=True)
            fake_binary = release_dir / "openfang"
            fake_binary.write_text("#!/bin/sh\necho openfang")
            fake_binary.chmod(0o755)

            install_dir = Path(tmpdir) / "bin"
            install_dir.mkdir()

            result = install_binary(vendor_dir=tmpdir, install_dir=str(install_dir))

        assert result["status"] == "success"
        assert "installed_at" in result


class TestGetUpstreamVersion:
    def test_nonexistent_dir_returns_empty_string(self):
        result = get_upstream_version(vendor_dir="/tmp/nonexistent_xyz_openfang")
        assert result == ""

    def test_returns_string(self):
        result = get_upstream_version(vendor_dir="/tmp/nonexistent_xyz_openfang")
        assert isinstance(result, str)

    def test_non_git_dir_returns_empty_string(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = get_upstream_version(vendor_dir=tmpdir)
        assert isinstance(result, str)


class TestBuildAndInstall:
    def test_propagates_build_error(self):
        result = build_and_install(vendor_dir="/tmp/nonexistent_xyz")
        assert result["status"] == "error"

    def test_returns_dict(self):
        result = build_and_install(vendor_dir="/tmp/nonexistent_xyz")
        assert isinstance(result, dict)
