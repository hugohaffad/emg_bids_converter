"""Write the dataset-level files"""

from pathlib import Path
from typing import Any, Sequence

from ._json import write_json, write_mapping
from ._tsv import select_columns, write_tsv
from ..core.schema import load
from ..models.dataset import Dataset
from ..models.dataset_description import DatasetDescription
from ..models.participants import Participant
from .emg.recording import write_recording
from .readme import write_readme


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


def write_dataset(root: Path, dataset: Dataset) -> list[Path]:
    """Write a whole dataset under root, which must not exist or be empty; return the written paths"""
    root = Path(root)
    if root.exists() and any(root.iterdir()):
        raise FileExistsError(f"{root} is not empty")
    root.mkdir(parents=True, exist_ok=True)

    description_path = root / "dataset_description.json"
    participants_tsv_path = root / "participants.tsv"
    participants_json_path = root / "participants.json"

    write_dataset_description_json(dataset.description, description_path)
    write_participants_tsv(dataset.participants, participants_tsv_path)
    write_participants_json(dataset.participants, participants_json_path)
    written = [description_path, participants_tsv_path, participants_json_path]
    written.append(write_readme(root, dataset.description.Name))

    for entities, recording in dataset.recordings:
        written += write_recording(root, entities, recording)
    return written
