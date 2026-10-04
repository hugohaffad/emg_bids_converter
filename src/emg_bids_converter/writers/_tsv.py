"""Serialize dataclass models to TSV files"""

from dataclasses import asdict
from pathlib import Path
from typing import Any, Sequence
import numpy as np

from ..core.schema import load


def _format(value: Any) -> str:
    """Convert a single cell value to its TSV representation"""
    if value is None:
        return "n/a"
    if isinstance(value, np.generic):
        value = value.item()
    text = str(value)
    if any(char in text for char in "\t\n\r"):
        raise ValueError(f"TSV value must not contain tabs or line breaks: {text!r}")
    return text


def write_tsv(rows: Sequence[Any], path: Path, keep: Sequence[str] = ()) -> None:
    """Write dataclass instances as the rows of a TSV file.
    A column whose values are all None is omitted, unless its name is listed in `keep`.
    """
    if not rows:
        raise ValueError("Cannot write a TSV file without rows")
    records = [asdict(row) for row in rows]
    columns = [
        name for name in records[0]
        if name in keep or any(record[name] is not None for record in records)
    ]
    header = [load().objects.columns[name].name for name in columns]
    lines = ["\t".join(header)]
    lines += ["\t".join(_format(record[name]) for name in columns) for record in records]
    with path.open("w", encoding="utf-8", newline="\n") as file:
        file.write("\n".join(lines) + "\n")