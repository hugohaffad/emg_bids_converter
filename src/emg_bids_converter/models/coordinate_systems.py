from dataclasses import dataclass

from ..core.validators import check_dataclass


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
        check_dataclass(self, required=("EMGCoordinateSystem", "EMGCoordinateUnits"))
