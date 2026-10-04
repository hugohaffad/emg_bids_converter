"""Write the files describing one EMG recording"""

from pathlib import Path
from typing import Sequence

from .._json import write_json
from .._tsv import write_tsv
from ...models.emg.channels import Channel
from ...models.emg.coordinate_systems import CoordinateSystem
from ...models.emg.electrodes import Electrode
from ...models.emg.entities import Entities
from ...models.emg.recording import Recording
from ...models.emg.sidecars import Sidecar
from .bdf import write_bdf
from .naming import build_directory, build_filename


def write_emg_json(sidecar: Sidecar, path: Path) -> None:
    """Write one recording's *_emg.json sidecar"""
    write_json(sidecar, path)


def write_channels_tsv(channels: Sequence[Channel], path: Path) -> None:
    """Write *_channels.tsv files"""
    write_tsv(channels, path)


def write_electrodes_tsv(electrodes: Sequence[Electrode], path: Path) -> None:
    """Write *_electrodes.tsv files"""
    write_tsv(electrodes, path, keep=("z",))


def write_coordsystem_json(coordinate_system: CoordinateSystem, path: Path) -> None:
    """Write *_coordsystem.json files"""
    write_json(coordinate_system, path)


def write_recording(root: Path, entities: Entities, recording: Recording) -> list[Path]:
    """Write the signal and sidecars of one recording under root; return the written paths"""
    directory = build_directory(Path(root), entities)
    directory.mkdir(parents=True, exist_ok=True)

    bdf_path = directory / build_filename(entities, "emg", ".bdf")
    sidecar_path = directory / build_filename(entities, "emg", ".json")
    channels_path = directory / build_filename(entities, "channels", ".tsv")

    write_bdf(recording, bdf_path)
    write_emg_json(recording.metadata, sidecar_path)
    write_channels_tsv(recording.channels, channels_path)
    written = [bdf_path, sidecar_path, channels_path]

    if recording.electrodes:
        electrodes_path = directory / build_filename(entities, "electrodes", ".tsv")
        write_electrodes_tsv(recording.electrodes, electrodes_path)
        written.append(electrodes_path)

    for space, coordinate_system in recording.coordinate_systems.items():
        coordsystem_path = directory / build_filename(entities, "coordsystem", ".json", space=space)
        write_coordsystem_json(coordinate_system, coordsystem_path)
        written.append(coordsystem_path)

    return written
