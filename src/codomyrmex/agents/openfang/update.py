"""Upstream sync utilities — pull latest openfang source and deploy.

Flow:
    1. update_submodule()     → git submodule update --remote --merge
    2. build_from_source()    → cargo build --release in vendor/openfang/
    3. install_binary()       → copy target/release/openfang → install_dir

Or call build_and_install() which runs all three steps.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .config import get_config
from .exceptions import OpenFangBuildError


def update_submodule(vendor_dir: str = "", timeout: int = 300) -> dict[str, str]:
    """Pull the latest openfang commits from upstream via git submodule."""
    cfg = get_config()
    target = vendor_dir or cfg.vendor_dir
    path = Path(target)
    if not path.exists():
        return {
            "status": "error",
            "message": (
                f"vendor dir not found: {target}. "
                "Run: git submodule update --init "
                "src/codomyrmex/agents/openfang/vendor/openfang"
            ),
        }
    # Walk up to find the git repo root (5 levels up from vendor/openfang)
    repo_root = path.parent.parent.parent.parent.parent
    try:
        result = subprocess.run(
            ["git", "submodule", "update", "--remote", "--merge", str(path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(repo_root),
        )
        return {
            "status": "success" if result.returncode == 0 else "error",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": str(result.returncode),
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": f"git submodule update timed out after {timeout}s",
        }
    except OSError as exc:
        return {"status": "error", "message": str(exc)}


def build_from_source(vendor_dir: str = "", timeout: int = 600) -> dict[str, str]:
    """Run cargo build --release inside the openfang vendor submodule."""
    cfg = get_config()
    target = vendor_dir or cfg.vendor_dir
    path = Path(target)
    cargo_toml = path / "Cargo.toml"
    if not cargo_toml.exists():
        return {
            "status": "error",
            "message": (
                f"Cargo.toml not found at {cargo_toml}. "
                "Is the submodule initialized? "
                "Run: git submodule update --init ..."
            ),
        }
    if not shutil.which("cargo"):
        return {
            "status": "error",
            "message": "cargo not found. Install Rust: https://rustup.rs/",
        }
    try:
        result = subprocess.run(
            ["cargo", "build", "--release"],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(path),
        )
        if result.returncode != 0:
            raise OpenFangBuildError(result.stderr)
        return {
            "status": "success",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "binary": str(path / "target" / "release" / "openfang"),
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": f"cargo build timed out after {timeout}s",
        }
    except OpenFangBuildError as exc:
        return {"status": "error", "message": str(exc)}


def install_binary(vendor_dir: str = "", install_dir: str = "") -> dict[str, str]:
    """Copy the compiled openfang binary to the install directory."""
    cfg = get_config()
    v_dir = Path(vendor_dir or cfg.vendor_dir)
    i_dir = Path(install_dir or cfg.install_dir)
    src = v_dir / "target" / "release" / "openfang"
    dst = i_dir / "openfang"
    if not src.exists():
        return {
            "status": "error",
            "message": (
                f"Compiled binary not found at {src}. "
                "Run build_from_source() first."
            ),
        }
    try:
        shutil.copy2(str(src), str(dst))
        dst.chmod(0o755)
        return {"status": "success", "installed_at": str(dst)}
    except PermissionError as exc:
        return {
            "status": "error",
            "message": (
                f"Permission denied copying to {dst}. "
                f"Try sudo or change OPENFANG_INSTALL_DIR. {exc}"
            ),
        }
    except OSError as exc:
        return {"status": "error", "message": str(exc)}


def build_and_install(vendor_dir: str = "", install_dir: str = "") -> dict[str, str]:
    """Convenience: build_from_source() then install_binary() in one call."""
    build = build_from_source(vendor_dir=vendor_dir)
    if build["status"] != "success":
        return build
    return install_binary(vendor_dir=vendor_dir, install_dir=install_dir)


def get_upstream_version(vendor_dir: str = "") -> str:
    """Return the git SHA of the currently checked-out upstream commit."""
    cfg = get_config()
    path = Path(vendor_dir or cfg.vendor_dir)
    if not path.exists():
        return ""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(path),
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except (subprocess.TimeoutExpired, OSError):
        return ""
