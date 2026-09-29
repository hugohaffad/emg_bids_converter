from dataclasses import asdict, dataclass

from ...core import check_metadata

_CONTEXT = {"datatype": "emg", "suffix": "coordsystem", "extension": ".json"}


@dataclass(frozen=True)
class CoordinateSystem:
    """Class implementing the fields of the *_coordsystem.json file"""
    EMGCoordinateSystem: str
    EMGCoordinateUnits: str
    EMGCoordinateSystemDescription: str | None = None
    ParentCoordinateSystem: str | None = None
    AnchorCoordinates: list[float] | None = None
    AnchorElectrode: str | None = None

    def __post_init__(self) -> None:
        check_metadata(asdict(self), _CONTEXT)
