"""Serialize a Recording's signal to a BDF+ file"""

from pathlib import Path

import numpy as np
import pyedflib
from pyedflib import highlevel

from ...models.emg.recording import Recording


def _physical_bounds(signal: np.ndarray) -> np.ndarray:
    """Symmetric physical range per channel, rounded up; 1.0 for an all-zero channel"""
    bounds = np.ceil(np.abs(signal).max(axis=1))
    return np.where(bounds == 0, 1.0, bounds)


def write_bdf(recording: Recording, path: Path) -> None:
    """Write the recording's signal to a BDF+ file"""
    signal = np.ascontiguousarray(recording.signal, dtype=np.float64)
    bounds = _physical_bounds(signal)
    headers = [
        highlevel.make_signal_header(
            label = channel.name__channels,
            dimension = channel.units,
            sample_frequency = recording.metadata.SamplingFrequency,
            physical_min = -float(bound),
            physical_max = float(bound),
            digital_min = -(2 ** 23),
            digital_max = 2 ** 23 - 1,
        )
        for channel, bound in zip(recording.channels, bounds)
    ]
    highlevel.write_edf(str(path), signal, headers, file_type=pyedflib.FILETYPE_BDFPLUS)