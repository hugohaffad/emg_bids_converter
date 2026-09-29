from dataclasses import asdict, dataclass

from ...core import check_row

_CONTEXT = {"datatype": "emg", "suffix": "electrodes", "extension": ".tsv"}


@dataclass(frozen=True)
class Electrode:
    """Class implementing the fields of the *_electrodes.tsv file (one row)"""
    name__electrodes: str
    x: float | None
    y: float | None
    z: float | None = None
    coordinate_system: str | None = None
    type__electrodes: str | None = None
    material: str | None = None
    impedance: float | None = None
    group__emg: float | str | None = None

    def __post_init__(self) -> None:
        check_row(asdict(self), _CONTEXT)