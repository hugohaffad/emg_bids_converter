import pytest

from emg_bids_converter.models.coordinate_systems import CoordinateSystem


def test_coordinate_system_valid():
    CoordinateSystem(EMGCoordinateSystem="Other", EMGCoordinateUnits="m")


def test_coordinate_system_system_cannot_be_empty():
    with pytest.raises(ValueError, match="EMGCoordinateSystem"):
        CoordinateSystem(EMGCoordinateSystem="", EMGCoordinateUnits="m")


def test_coordinate_system_system_enum():
    with pytest.raises(ValueError, match="EMGCoordinateSystem"):
        CoordinateSystem(EMGCoordinateSystem="Scanner", EMGCoordinateUnits="m")


def test_coordinate_system_units_enum():
    with pytest.raises(ValueError, match="EMGCoordinateUnits"):
        CoordinateSystem(EMGCoordinateSystem="Other", EMGCoordinateUnits="inches")


def test_coordinate_system_accepts_valid_units():
    CoordinateSystem(EMGCoordinateSystem="Other", EMGCoordinateUnits="mm")


def test_coordinate_system_anchor_coordinates_valid():
    CoordinateSystem(EMGCoordinateSystem="Other", EMGCoordinateUnits="m",
                      AnchorCoordinates=[1.0, 2.0, 3.0])


def test_coordinate_system_anchor_coordinates_rejects_empty_list():
    with pytest.raises(ValueError, match="AnchorCoordinates"):
        CoordinateSystem(EMGCoordinateSystem="Other", EMGCoordinateUnits="m", AnchorCoordinates=[])


def test_coordinate_system_anchor_coordinates_rejects_too_many_items():
    with pytest.raises(ValueError, match="AnchorCoordinates"):
        CoordinateSystem(EMGCoordinateSystem="Other", EMGCoordinateUnits="m",
                          AnchorCoordinates=[1.0, 2.0, 3.0, 4.0])
