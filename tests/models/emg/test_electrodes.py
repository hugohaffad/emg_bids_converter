import pytest

from emg_bids_converter.models.emg.electrodes import Electrode


def test_electrode_valid():
    Electrode(name__electrodes="e1", x=1.0, y=2.0)


def test_electrode_name_cannot_be_empty():
    with pytest.raises(ValueError, match="name__electrodes"):
        Electrode(name__electrodes=" ", x=1.0, y=2.0)


def test_electrode_x_must_be_number():
    with pytest.raises(TypeError, match="x"):
        Electrode(name__electrodes="e1", x="left", y=2.0)


def test_electrode_x_empty_string_raises_value_error():
    with pytest.raises(ValueError, match="x"):
        Electrode(name__electrodes="e1", x="", y=2.0)


def test_electrode_group_accepts_string_or_number():
    Electrode(name__electrodes="e1", x=1.0, y=2.0, group__emg="grid1")
    Electrode(name__electrodes="e1", x=1.0, y=2.0, group__emg=1)


def test_electrode_impedance_must_be_number():
    with pytest.raises(TypeError, match="impedance"):
        Electrode(name__electrodes="e1", x=1.0, y=2.0, impedance="high")


def test_electrode_position_can_be_unknown():
    Electrode(name__electrodes="e1", x=None, y=None)


def test_electrode_position_must_be_given():
    with pytest.raises(TypeError):
        Electrode(name__electrodes="e1")