import pytest

from emg_bids_converter.models.coordinate_systems import CoordinateSystem

_DESCRIPTION = "Grid-relative positions, origin at the first electrode"


def _coordsys(**overrides):
    fields = dict(EMGCoordinateSystem="Other", EMGCoordinateUnits="m",
                  EMGCoordinateSystemDescription=_DESCRIPTION)
    fields.update(overrides)
    return CoordinateSystem(**fields)


def test_coordinate_system_valid():
    _coordsys()


def test_coordinate_system_system_cannot_be_empty():
    with pytest.raises(ValueError, match="EMGCoordinateSystem"):
        _coordsys(EMGCoordinateSystem="")


def test_coordinate_system_system_enum():
    with pytest.raises(ValueError, match="EMGCoordinateSystem"):
        _coordsys(EMGCoordinateSystem="Scanner")


def test_coordinate_system_units_enum():
    with pytest.raises(ValueError, match="EMGCoordinateUnits"):
        _coordsys(EMGCoordinateUnits="inches")


def test_coordinate_system_accepts_valid_units():
    _coordsys(EMGCoordinateUnits="mm")


def test_coordinate_system_anchor_coordinates_valid():
    _coordsys(AnchorCoordinates=[1.0, 2.0, 3.0])


def test_coordinate_system_anchor_coordinates_rejects_empty_list():
    with pytest.raises(ValueError, match="AnchorCoordinates"):
        _coordsys(AnchorCoordinates=[])


def test_coordinate_system_anchor_coordinates_rejects_too_many_items():
    with pytest.raises(ValueError, match="AnchorCoordinates"):
        _coordsys(AnchorCoordinates=[1.0, 2.0, 3.0, 4.0])


def test_coordinate_system_other_requires_description():
    with pytest.raises(ValueError, match="EMGCoordinateSystemDescription"):
        CoordinateSystem(EMGCoordinateSystem="Other", EMGCoordinateUnits="m")


def test_coordinate_system_parent_requires_anchor():
    with pytest.raises(ValueError, match="AnchorCoordinates"):
        _coordsys(ParentCoordinateSystem="forearm")


def test_coordinate_system_parent_with_anchor():
    _coordsys(ParentCoordinateSystem="forearm", AnchorCoordinates=[0.0, 0.0, 0.0], AnchorElectrode="e1")
