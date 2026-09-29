import numpy as np
import pytest

from emg_bids_converter.models.emg.channels import Channel
from emg_bids_converter.models.emg.coordinate_systems import CoordinateSystem
from emg_bids_converter.models.emg.electrodes import Electrode
from emg_bids_converter.models.emg.recording import Recording
from emg_bids_converter.models.emg.sidecars import Sidecar


def _channel(name, **overrides):
    return Channel(name__channels=name, type__channels=overrides.pop("type", "EMG"), units="mV", **overrides)


def _coordsys(**overrides):
    fields = dict(EMGCoordinateSystem="Other", EMGCoordinateUnits="mm",
                  EMGCoordinateSystemDescription="Grid-relative positions")
    fields.update(overrides)
    return CoordinateSystem(**fields)


def _sidecar(**overrides):
    fields = dict(EMGPlacementScheme="Measured", EMGReference="REF", SamplingFrequency=2000.0,
                  PowerLineFrequency=50.0, RecordingType="continuous", SoftwareFilters="n/a", TaskName="mvc")
    fields.update(overrides)
    return Sidecar(**fields)


def _recording(channels=None, electrodes=(), coordinate_systems=None, metadata=None, signal=None):
    channels = [_channel("ch1"), _channel("ch2")] if channels is None else channels
    return Recording(
        signal=np.zeros((len(channels), 10)) if signal is None else signal,
        channels=list(channels),
        electrodes=list(electrodes),
        coordinate_systems={} if coordinate_systems is None else coordinate_systems,
        metadata=_sidecar() if metadata is None else metadata,
    )


def test_recording_valid():
    _recording()


def test_recording_signal_must_be_2d():
    with pytest.raises(ValueError, match="2-D"):
        _recording(signal=np.zeros(20))


def test_recording_signal_rows_match_channels():
    with pytest.raises(ValueError, match="3 rows but 2 channels"):
        _recording(signal=np.zeros((3, 10)))


def test_recording_rejects_duplicate_channel_names():
    with pytest.raises(ValueError, match="duplicate channel"):
        _recording(channels=[_channel("ch1"), _channel("ch1")])


def test_recording_rejects_duplicate_electrode_in_same_group():
    with pytest.raises(ValueError, match="duplicate electrode"):
        _recording(electrodes=[Electrode(name__electrodes="e1", x=0.0, y=0.0, group__emg="grid1"),
                               Electrode(name__electrodes="e1", x=1.0, y=0.0, group__emg="grid1")])


def test_recording_accepts_same_electrode_name_in_different_groups():
    _recording(electrodes=[Electrode(name__electrodes="e1", x=0.0, y=0.0, group__emg="grid1"),
                           Electrode(name__electrodes="e1", x=0.0, y=0.0, group__emg="grid2")])


def test_recording_emg_channel_count_must_match():
    _recording(metadata=_sidecar(EMGChannelCount=2))
    with pytest.raises(ValueError, match="EMGChannelCount"):
        _recording(metadata=_sidecar(EMGChannelCount=3))


def test_recording_emg_channel_count_ignores_other_types():
    _recording(channels=[_channel("ch1"), _channel("TRIG", type="TRIG")], metadata=_sidecar(EMGChannelCount=1))


def test_recording_reference_may_be_bipolar():
    _recording(channels=[_channel("ch1", reference__emg="bipolar"), _channel("ch2")])


def test_recording_reference_must_be_a_known_electrode():
    electrodes = [Electrode(name__electrodes="REF", x=0.0, y=0.0)]
    _recording(channels=[_channel("ch1", reference__emg="REF"), _channel("ch2")], electrodes=electrodes)
    with pytest.raises(ValueError, match="reference"):
        _recording(channels=[_channel("ch1", reference__emg="E99"), _channel("ch2")], electrodes=electrodes)


def test_recording_electrode_coordinate_system_must_be_declared():
    electrodes = [Electrode(name__electrodes="e1", x=0.0, y=0.0, coordinate_system="grid1")]
    _recording(electrodes=electrodes, coordinate_systems={"grid1": _coordsys()})
    with pytest.raises(ValueError, match="coordinate_system"):
        _recording(electrodes=electrodes, coordinate_systems={})


def test_recording_parent_coordinate_system_must_be_declared():
    child = _coordsys(ParentCoordinateSystem="forearm", AnchorCoordinates=[0.0, 0.0], AnchorElectrode="e1")
    _recording(coordinate_systems={"grid1": child, "forearm": _coordsys()})
    with pytest.raises(ValueError, match="ParentCoordinateSystem"):
        _recording(coordinate_systems={"grid1": child})
