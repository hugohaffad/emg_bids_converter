"""Serialize dataclass models to TSV files, and read them back"""

import typing
from dataclasses import asdict, fields
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


def select_columns(rows: Sequence[Any], keep: Sequence[str] = ()) -> list[str]:
    """Field names written as columns: those with at least one value, plus those listed in `keep`"""
    if not rows:
        raise ValueError("Cannot select columns without rows")
    records = [asdict(row) for row in rows]
    return [
        name for name in records[0]
        if name in keep or any(record[name] is not None for record in records)
    ]


def write_tsv(rows: Sequence[Any], path: Path, keep: Sequence[str] = ()) -> None:
    """Write dataclass instances as the rows of a TSV file.
    A column whose values are all None is omitted, unless its name is listed in `keep`.
    """
    columns = select_columns(rows, keep)
    records = [asdict(row) for row in rows]
    header = [load().objects.columns[name].name for name in columns]
    lines = ["\t".join(header)]
    lines += ["\t".join(_format(record[name]) for name in columns) for record in records]
    with path.open("w", encoding="utf-8", newline="\n") as file:
        file.write("\n".join(lines) + "\n")


def _parse(text: str, annotation: Any) -> Any:
    """Convert one TSV cell back to the type of its field: n/a -> None, then str, float or int"""
    if text == "n/a":
        return None
    kinds = typing.get_args(annotation) or (annotation,)
    if str in kinds:
        return text
    if float in kinds:
        return float(text)
    if int in kinds:
        return int(text)
    return text


def read_tsv(path: Path, cls: type) -> list[Any]:
    """Read the rows of a TSV file written by write_tsv back into instances of the dataclass cls"""
    columns = load().objects.columns
    field_of = {columns[field.name].name: field.name for field in fields(cls)}
    hints = typing.get_type_hints(cls)

    lines = path.read_text(encoding="utf-8").splitlines()
    header = lines[0].split("\t")
    unknown = [column for column in header if column not in field_of]
    if unknown:
        raise ValueError(f"{path.name}: column(s) {unknown} are not fields of {cls.__name__}")

    rows = []
    for line in lines[1:]:
        cells = dict(zip(header, line.split("\t")))
        rows.append(cls(**{field_of[c]: _parse(text, hints[field_of[c]]) for c, text in cells.items()}))
    return rows
