"""Write the dataset-level files"""

from pathlib import Path
from typing import Any, Sequence

from ._json import write_json, write_mapping
from ._tsv import select_columns, write_tsv
from ..core.schema import load
from ..models.dataset_description import DatasetDescription
from ..models.participants import Participant


def write_dataset_description_json(description: DatasetDescription, path: Path) -> None:
    """Write the dataset_description.json file"""
    write_json(description, path)


def write_participants_tsv(participants: Sequence[Participant], path: Path) -> None:
    """Write the participants.tsv file"""
    write_tsv(participants, path)


def _to_plain(value: Any) -> Any:
    """Convert schema Namespaces to plain dicts"""
    if hasattr(value, "items"):
        return {key: _to_plain(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_plain(item) for item in value]
    return value


def write_participants_json(participants: Sequence[Participant], path: Path) -> None:
    """Write participants.json"""
    columns = load().objects.columns
    data = {}
    for name in select_columns(participants):
        definition = columns[name].get("definition")
        if definition is not None:
            data[columns[name].name] = _to_plain(definition)
    write_mapping(data, path)
