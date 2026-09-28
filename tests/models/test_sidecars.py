import pytest

from emg_bids_converter.models.sidecars import Sidecar


def _sidecar(**overrides):
    fields = dict(
        EMGPlacementScheme="Measured",
        EMGReference="n/a",
        SamplingFrequency=2000.0,
        PowerLineFrequency=50.0,
        RecordingType="continuous",
        SoftwareFilters="n/a",
        TaskName="rest",
    )
    fields.update(overrides)
    return Sidecar(**fields)


def test_sidecar_valid():
    _sidecar()


def test_sidecar_recording_type_enum():
    with pytest.raises(ValueError, match="RecordingType"):
        _sidecar(RecordingType="streaming")


def test_sidecar_placement_scheme_enum():
    with pytest.raises(ValueError, match="EMGPlacementScheme"):
        _sidecar(EMGPlacementScheme="Somewhere")


def test_sidecar_sampling_frequency_must_be_number():
    with pytest.raises(TypeError, match="SamplingFrequency"):
        _sidecar(SamplingFrequency="fast")


def test_sidecar_task_name_cannot_be_empty():
    with pytest.raises(ValueError, match="TaskName"):
        _sidecar(TaskName="")
