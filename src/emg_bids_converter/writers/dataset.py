"""Write the dataset-level files"""

from pathlib import Path
from typing import Sequence

from ._json import write_json
from ._tsv import write_tsv
from ..models.dataset_description import DatasetDescription
from ..models.participants import Participant


def write_dataset_description_json(description: DatasetDescription, path: Path) -> None:
    """Write the dataset_description.json file"""
    write_json(description, path)


def write_participants_tsv(participants: Sequence[Participant], path: Path) -> None:
    """Write the participants.tsv file"""
    write_tsv(participants, path)
