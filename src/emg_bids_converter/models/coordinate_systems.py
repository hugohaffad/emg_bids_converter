from dataclasses import dataclass


@dataclass(frozen=True)
class CoordinateSystem:
    """Class implementing the fields of the *_coordsystem.json file"""
    EMGCoordinateSystem: str
    EMGCoordinateUnits: str
    EMGCoordinateSystemDescription: str | None = None
    ParentCoordinateSystem: str | None = None
    AnchorCoordinates: list[float] | None = None
    AnchorElectrode: str | None = None
