from dataclasses import dataclass


@dataclass(frozen=True)
class Electrode:
    """Class implementing the fields of the *_electrodes.tsv file (one row)"""
    name__electrodes: str
    x: float
    y: float
    z: float | None = None
    coordinate_system: str | None = None
    type__electrodes: str | None = None
    material: str | None = None
    impedance: float | None = None
    group__emg: float | str | None = None
