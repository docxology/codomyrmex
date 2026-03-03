"""MCP tools for the file_system module."""

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="file_system")
def file_system_read(path: str) -> dict:
    """Read a file and return its contents.

    Args:
        path: Absolute or relative path to the file to read.

    Returns:
        Dictionary with the file contents and metadata.
    """
    try:
        from codomyrmex.file_system import FileSystemManager

        fs = FileSystemManager()
        content = fs.read_file(path)
        return {
            "status": "success",
            "path": str(path),
            "content": content,
            "size_bytes": (
                len(content.encode("utf-8"))
                if isinstance(content, str)
                else len(content)
            ),
        }
    except FileNotFoundError:
        return {"status": "error", "message": f"File not found: {path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="file_system")
def file_system_list_directory(
    path: str = ".",
    recursive: bool = False,
) -> dict:
    """List entries in a directory.

    Args:
        path: Directory path to list (default: current working directory).
        recursive: If True, recurse into subdirectories.

    Returns:
        Dictionary with a list of file/directory paths.
    """
    try:
        from codomyrmex.file_system import FileSystemManager

        fs = FileSystemManager()
        entries = fs.list_dir(path, recursive=recursive)
        return {
            "status": "success",
            "path": str(path),
            "recursive": recursive,
            "entries": [str(e) for e in entries],
            "count": len(entries),
        }
    except FileNotFoundError:
        return {"status": "error", "message": f"Directory not found: {path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
