"""End-to-end: models -> write_dataset -> files on disk -> (optionally) bids-validator.

The bids-validator step runs only if the `bids-validator` executable is on the PATH
(deno install -ERWN -g -n bids-validator jsr:@bids/validator); otherwise it is skipped.
The OTB4 test runs on the file given by EMG_BIDS_OTB4, or else the first data/*.otb4 of the repository.
"""

import os
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest
from pyedflib import highlevel

from emg_bids_converter.models.dataset import Dataset
from emg_bids_converter.models.dataset_description import DatasetDescription
from emg_bids_converter.models.emg.entities import Entities
from emg_bids_converter.models.participants import Participant
from emg_bids_converter.readers import otb4
from emg_bids_converter.writers.dataset import write_dataset

_REPO_ROOT = Path(__file__).resolve().parents[1]


def _bids_validator(root: Path) -> None:
    """Run bids-validator on root and fail the test on any error; skip if it is not installed"""
    executable = shutil.which("bids-validator")
    if executable is None:
        pytest.skip("bids-validator is not installed")
    result = subprocess.run([executable, str(root)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def _otb4_sample() -> Path | None:
    if os.environ.get("EMG_BIDS_OTB4"):
        return Path(os.environ["EMG_BIDS_OTB4"])
    return next(iter(sorted((_REPO_ROOT / "data").glob("*.otb4"))), None)


def test_synthetic_dataset_files(tmp_path, make_dataset):
    root = tmp_path / "ds"
    written = write_dataset(root, make_dataset(subjects=("01", "02")))

    assert sorted(str(p.relative_to(root)) for p in written) == sorted([
        "dataset_description.json",
        "participants.tsv",
        "participants.json",
        "README.md",
        "sub-01/emg/sub-01_task-mvc_emg.bdf",
        "sub-01/emg/sub-01_task-mvc_emg.json",
        "sub-01/emg/sub-01_task-mvc_channels.tsv",
        "sub-02/emg/sub-02_task-mvc_emg.bdf",
        "sub-02/emg/sub-02_task-mvc_emg.json",
        "sub-02/emg/sub-02_task-mvc_channels.tsv",
    ])
    assert (root / "participants.tsv").read_text(encoding="utf-8").splitlines()[1:] == [
        "sub-01\t30.0\tM",
        "sub-02\t30.0\tM",
    ]


def test_synthetic_bdf_round_trip(tmp_path, make_dataset):
    """The BDF read back gives the same signal, labels, units and rate, up to 24-bit quantization"""
    dataset = make_dataset()
    root = tmp_path / "ds"
    write_dataset(root, dataset)
    _, recording = dataset.recordings[0]

    signals, headers, _ = highlevel.read_edf(str(root / "sub-01/emg/sub-01_task-mvc_emg.bdf"))

    assert [h["label"] for h in headers] == [c.name__channels for c in recording.channels]
    assert [h["dimension"] for h in headers] == [c.units for c in recording.channels]
    assert all(h["sample_frequency"] == recording.metadata.SamplingFrequency for h in headers)
    # physical range ±1 mV over 2**24 levels: one step is about 1.2e-7 mV
    np.testing.assert_allclose(np.asarray(signals), recording.signal, rtol=0, atol=1e-6)


def test_synthetic_dataset_is_valid_bids(tmp_path, make_dataset):
    root = tmp_path / "ds"
    write_dataset(root, make_dataset(subjects=("01", "02")))
    _bids_validator(root)


def test_otb4_dataset_is_valid_bids(tmp_path):
    path = _otb4_sample()
    if path is None or not path.is_file():
        pytest.skip("no OTB4 sample (set EMG_BIDS_OTB4 or put a file in data/)")

    recording = otb4.read(path, task_name="mvc", emg_reference="Not specified (end-to-end test)")
    dataset = Dataset(
        description=DatasetDescription(Name="OTB4 end-to-end test", BIDSVersion="1.11.1"),
        participants=[Participant(participant_id="sub-01")],
        recordings=[(Entities(subject="01", task="mvc"), recording)],
    )
    root = tmp_path / "ds"
    write_dataset(root, dataset)

    signals, headers, _ = highlevel.read_edf(str(root / "sub-01/emg/sub-01_task-mvc_emg.bdf"))
    assert len(headers) == len(recording.channels)
    n_samples = recording.signal.shape[1]
    # BDF stores float32 OTB4 data with a 24-bit step of (2 * bound) / 2**24
    bounds = np.ceil(np.abs(recording.signal).max(axis=1, keepdims=True))
    np.testing.assert_allclose(np.asarray(signals)[:, :n_samples], recording.signal, rtol=0, atol=float(bounds.max()) / 2**22)

    _bids_validator(root)
