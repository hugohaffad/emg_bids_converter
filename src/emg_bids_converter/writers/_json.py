"""Serialize dataclass models to JSON files."""

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any
import numpy as np


def _to_builtin(value: Any) -> Any:
    """Convert numpy objects to native Python types."""
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def write_json(obj: Any, path: Path) -> None:
    """Write a dataclass instance to a JSON file, leaving out the fields that are None."""
    write_mapping({key: value for key, value in asdict(obj).items() if value is not None}, path)


def write_mapping(data: dict, path: Path) -> None:
    """Write a dict to a JSON file."""
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False, allow_nan=False, default=_to_builtin)
        file.write("\n")
