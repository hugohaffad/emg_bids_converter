"""Factories of valid models, shared by the writer and end-to-end tests."""

import numpy as np
import pytest

from emg_bids_converter.models.dataset import Dataset
from emg_bids_converter.models.dataset_description import DatasetDescription
from emg_bids_converter.models.emg.channels import Channel
from emg_bids_converter.models.emg.entities import Entities
from emg_bids_converter.models.emg.recording import Recording
from emg_bids_converter.models.emg.sidecars import Sidecar
from emg_bids_converter.models.participants import Participant

SAMPLING_FREQUENCY = 2000.0


def _sine_signal(n_channels: int, seconds: float) -> np.ndarray:
    """(n_channels, n_samples) sines of 0.5 mV amplitude, one frequency per channel"""
    t = np.arange(int(seconds * SAMPLING_FREQUENCY)) / SAMPLING_FREQUENCY
    return np.vstack([0.5 * np.sin(2 * np.pi * (10 + 5 * i) * t) for i in range(n_channels)])


@pytest.fixture
def make_recording():
    def factory(n_channels: int = 4, seconds: float = 2.0, **recording_fields) -> Recording:
        channels = [
            Channel(name__channels=f"ch{i + 1}", type__channels="EMG", units="mV", group__emg="IN1")
            for i in range(n_channels)
        ]
        metadata = Sidecar(
            EMGPlacementScheme="Other",
            EMGPlacementSchemeDescription="Synthetic test recording",
            EMGReference="n/a",
            SamplingFrequency=SAMPLING_FREQUENCY,
            PowerLineFrequency=50.0,
            RecordingType="continuous",
            SoftwareFilters="n/a",
            TaskName="mvc",
            EMGChannelCount=n_channels,
            RecordingDuration=seconds,
        )
        fields = dict(
            signal=_sine_signal(n_channels, seconds),
            channels=channels,
            electrodes=[],
            coordinate_systems={},
            metadata=metadata,
        )
        fields.update(recording_fields)
        return Recording(**fields)
    return factory


@pytest.fixture
def make_dataset(make_recording):
    def factory(subjects: tuple[str, ...] = ("01",)) -> Dataset:
        return Dataset(
            description=DatasetDescription(Name="Synthetic EMG dataset", BIDSVersion="1.11.1"),
            participants=[Participant(participant_id=f"sub-{s}", age=30.0, sex="M") for s in subjects],
            recordings=[(Entities(subject=s, task="mvc"), make_recording()) for s in subjects],
        )
    return factory
