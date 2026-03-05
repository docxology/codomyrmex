"""MCP tools for the documents module."""

import os

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="documents")
def document_read(
    path: str,
    encoding: str = "utf-8",
    max_bytes: int = 1_000_000,
) -> dict:
    """Read a document file and return its content.

    Args:
        path: Absolute or relative path to the document file
        encoding: Text encoding (default: utf-8)
        max_bytes: Maximum bytes to read (default: 1MB)

    Returns:
        Dictionary with document content, size, and format metadata.
    """
    try:
        path = os.path.expanduser(path)
        if not os.path.isfile(path):
            return {"status": "error", "message": f"File not found: {path}"}

        size = os.path.getsize(path)
        if size > max_bytes:
            return {
                "status": "error",
                "message": f"File too large ({size} bytes > {max_bytes} limit). Use max_bytes to increase.",
                "size": size,
            }

        ext = os.path.splitext(path)[1].lower()
        format_map = {
            ".md": "markdown",
            ".markdown": "markdown",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".txt": "text",
            ".html": "html",
            ".xml": "xml",
            ".csv": "csv",
            ".py": "python",
            ".toml": "toml",
        }
        fmt = format_map.get(ext, "text")

        with open(path, encoding=encoding, errors="replace") as f:
            content = f.read()

        return {
            "status": "success",
            "path": path,
            "format": fmt,
            "size": size,
            "encoding": encoding,
            "content": content,
            "line_count": content.count("\n") + 1,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="documents")
def document_list(
    directory: str = ".",
    recursive: bool = False,
    formats: str = "md,txt,json,yaml,html,xml,csv",
) -> dict:
    """List document files in a directory.

    Args:
        directory: Directory path to scan (default: current directory)
        recursive: Whether to scan subdirectories recursively
        formats: Comma-separated list of file extensions to include

    Returns:
        Dictionary with list of document files and summary statistics.
    """
    try:
        directory = os.path.expanduser(directory)
        if not os.path.isdir(directory):
            return {"status": "error", "message": f"Directory not found: {directory}"}

        exts = {f".{e.strip().lstrip('.')}" for e in formats.split(",")}
        files = []

        if recursive:
            for root, _, fnames in os.walk(directory):
                for fname in fnames:
                    if os.path.splitext(fname)[1].lower() in exts:
                        full = os.path.join(root, fname)
                        files.append(
                            {
                                "path": full,
                                "name": fname,
                                "size": os.path.getsize(full),
                                "format": os.path.splitext(fname)[1].lstrip("."),
                            }
                        )
        else:
            for fname in os.listdir(directory):
                if os.path.splitext(fname)[1].lower() in exts:
                    full = os.path.join(directory, fname)
                    if os.path.isfile(full):
                        files.append(
                            {
                                "path": full,
                                "name": fname,
                                "size": os.path.getsize(full),
                                "format": os.path.splitext(fname)[1].lstrip("."),
                            }
                        )

        files.sort(key=lambda x: x["name"])
        return {
            "status": "success",
            "directory": directory,
            "count": len(files),
            "files": files,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="documents")
def document_search(
    query: str,
    directory: str = ".",
    recursive: bool = True,
    formats: str = "md,txt",
    max_results: int = 20,
) -> dict:
    """Search for a text pattern across document files in a directory.

    Args:
        query: Text pattern to search for (case-insensitive)
        directory: Directory to search in (default: current directory)
        recursive: Whether to search subdirectories
        formats: Comma-separated file extensions to search
        max_results: Maximum number of matching files to return

    Returns:
        Dictionary with matching files, match counts, and excerpt snippets.
    """
    import re

    try:
        directory = os.path.expanduser(directory)
        if not os.path.isdir(directory):
            return {"status": "error", "message": f"Directory not found: {directory}"}

        exts = {f".{e.strip().lstrip('.')}" for e in formats.split(",")}
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        matches = []

        def _scan(dirpath: str) -> None:
            for entry in os.scandir(dirpath):
                if entry.is_file() and os.path.splitext(entry.name)[1].lower() in exts:
                    try:
                        with open(entry.path, encoding="utf-8", errors="replace") as f:
                            content = f.read()
                        hits = pattern.findall(content)
                        if hits:
                            lines = content.split("\n")
                            excerpts = [
                                line.strip() for line in lines if pattern.search(line)
                            ][:3]
                            matches.append(
                                {
                                    "path": entry.path,
                                    "match_count": len(hits),
                                    "excerpts": excerpts,
                                }
                            )
                    except OSError:
                        pass
                elif recursive and entry.is_dir() and not entry.name.startswith("."):
                    _scan(entry.path)

        _scan(directory)
        matches.sort(key=lambda x: -x["match_count"])

        return {
            "status": "success",
            "query": query,
            "total_matches": len(matches),
            "results": matches[:max_results],
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
