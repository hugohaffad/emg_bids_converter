"""End-to-end: OTB4 file -> Recording -> write_dataset -> BDF read back -> bids-validator.

Runs on every data/*.otb4 file of the repository, or on the single file given by EMG_BIDS_OTB4.
The bids-validator step needs the `bids-validator` executable on the PATH
(deno install -ERWN -g -n bids-validator jsr:@bids/validator); otherwise the test is skipped.
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


def _otb4_samples() -> list[Path]:
    if os.environ.get("EMG_BIDS_OTB4"):
        return [Path(os.environ["EMG_BIDS_OTB4"])]
    return sorted((_REPO_ROOT / "data").glob("*.otb4"))


def _bids_validator(root: Path) -> None:
    """Run bids-validator on root and fail the test on any error; skip if it is not installed"""
    executable = shutil.which("bids-validator")
    if executable is None:
        pytest.skip("bids-validator is not installed")
    result = subprocess.run([executable, str(root)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("path", _otb4_samples(), ids=lambda p: p.name)
def test_otb4_dataset_is_valid_bids(tmp_path, path):
    recording = otb4.read(path, task_name="mvc", emg_reference="Not specified (end-to-end test)")
    dataset = Dataset(
        description=DatasetDescription(Name="OTB4 end-to-end test", BIDSVersion="1.11.1"),
        participants=[Participant(participant_id="sub-01")],
        recordings=[(Entities(subject="01", task="mvc"), recording)],
    )
    root = tmp_path / "ds"
    write_dataset(root, dataset)

    # The BDF read back gives the reader's signal, up to 24-bit quantization
    signals, headers, _ = highlevel.read_edf(str(root / "sub-01/emg/sub-01_task-mvc_emg.bdf"))
    assert [h["label"] for h in headers] == [c.name__channels for c in recording.channels]
    n_samples = recording.signal.shape[1]
    bound = float(np.ceil(np.abs(recording.signal).max()))
    np.testing.assert_allclose(np.asarray(signals)[:, :n_samples], recording.signal, rtol=0, atol=bound / 2**22)

    _bids_validator(root)
