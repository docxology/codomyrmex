"""Atomic JSON file writes shared by the workflow and project managers."""

import json
import os
import uuid
from pathlib import Path
from typing import Any


def write_json_atomic(path: Path, data: Any) -> None:
    """Write ``data`` to ``path`` as indented JSON, atomically.

    ``data`` is serialised before the disk is touched, so a value that is not
    JSON-serialisable (``TypeError``) or a non-finite float (``ValueError``)
    leaves ``path`` unchanged. The text goes to a uniquely named temporary file
    in the same directory, which then replaces ``path`` with
    :func:`os.replace`, so readers never see a partially written file.

    Raises:
        TypeError: If ``data`` contains a value JSON cannot represent.
        ValueError: If ``data`` contains NaN or infinity, or a circular
            reference.
        OSError: If the file cannot be written.
    """
    text = json.dumps(data, indent=2, allow_nan=False) + "\n"
    tmp_path = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with open(tmp_path, "x", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_path, path)
    except BaseException:
        tmp_path.unlink(missing_ok=True)
        raise
