from importlib.metadata import version
from pathlib import Path

from .core.schema import load
from .models.dataset_description import DatasetDescription
from .models.emg.entities import Entities
from .readers import read
from .writers.dataset import add_recording, init_dataset

PACKAGE = "emg-bids-converter"
CODE_URL = "https://github.com/hugohaffad/emg_bids_converter"


def create_dataset(root: Path, name: str, authors: list[str] | None = None,
                   license: str | None = None) -> list[Path]:
    """Create an empty BIDS dataset under root; return the written paths"""
    description = DatasetDescription(
        Name=name,
        BIDSVersion=load()["bids_version"],
        Authors=authors,
        License=license,
        GeneratedBy=[{"Name": PACKAGE, "Version": version(PACKAGE), "CodeURL": CODE_URL}],
    )
    return init_dataset(root, description)


def convert_recording(root: Path, file: Path, entities: Entities, emg_reference: str,
                      powerline_frequency: float = 50.0) -> list[Path]:
    """Read one recording file and add it to the dataset under root; return the written paths"""
    recording = read(
        file,
        task_name=entities.task,
        emg_reference=emg_reference,
        powerline_frequency=powerline_frequency,
    )
    return add_recording(root, entities, recording)
