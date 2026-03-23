"""Scaffold a minimal FastMCP server package for Hermes/Codomyrmex workflows."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return slug or "fastmcp_server"


def scaffold_fastmcp(
    *,
    output_dir: str,
    server_name: str,
    force: bool = False,
) -> dict[str, str]:
    """Create a FastMCP scaffold package and return key generated paths."""
    output_path = Path(output_dir).expanduser().resolve()
    module_name = _slug(server_name)
    package_dir = output_path / module_name
    package_dir.mkdir(parents=True, exist_ok=True)

    server_file = package_dir / "server.py"
    readme_file = package_dir / "README.md"
    pyproject_file = package_dir / "pyproject.toml"
    init_file = package_dir / "__init__.py"

    files = {
        server_file: (
            "from __future__ import annotations\n\n"
            "from fastmcp import FastMCP\n\n"
            f"mcp = FastMCP(name={server_name!r})\n\n\n"
            "@mcp.tool()\n"
            "def ping(message: str = 'pong') -> str:\n"
            '    """Simple health probe tool."""\n'
            "    return message\n\n\n"
            "if __name__ == '__main__':\n"
            "    mcp.run()\n"
        ),
        readme_file: (
            f"# {server_name}\n\n"
            "Generated FastMCP scaffold for Hermes/Codomyrmex integration.\n\n"
            "## Run\n\n"
            "```bash\n"
            "uv run python -m "
            f"{module_name}.server\n"
            "```\n"
        ),
        pyproject_file: (
            "[project]\n"
            f'name = "{module_name}"\n'
            'version = "0.1.0"\n'
            f'description = "FastMCP scaffold for {server_name}"\n'
            'requires-python = ">=3.11"\n'
            'dependencies = ["fastmcp>=2.0.0"]\n'
        ),
        init_file: "__all__ = []\n",
    }

    for path, content in files.items():
        if path.exists() and not force:
            msg = (
                f"Refusing to overwrite existing file: {path}. "
                "Use force=True/--force to overwrite."
            )
            raise FileExistsError(msg)
        path.write_text(content, encoding="utf-8")

    return {
        "output_dir": str(output_path),
        "package_dir": str(package_dir),
        "module_name": module_name,
        "server_file": str(server_file),
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scaffold a FastMCP server package.")
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory where the package folder will be generated.",
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Human-readable server name (used in README and FastMCP metadata).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite generated files if they already exist.",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    result = scaffold_fastmcp(
        output_dir=args.output_dir,
        server_name=args.name,
        force=args.force,
    )
    print(json.dumps({"status": "success", **result}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
