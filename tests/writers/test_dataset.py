import json

import pytest

from emg_bids_converter.models.participants import Participant
from emg_bids_converter.writers.dataset import write_dataset, write_participants_json


def test_participants_json_describes_the_written_columns(tmp_path):
    path = tmp_path / "participants.json"
    write_participants_json([Participant(participant_id="sub-01", age=30.0, sex="M")], path)
    data = json.loads(path.read_text(encoding="utf-8"))
    # participant_id has no definition in the schema; handedness is not written (all None)
    assert set(data) == {"age", "sex"}
    assert data["age"]["Units"] == "year"


def test_write_dataset_refuses_a_non_empty_root(tmp_path, make_dataset):
    (tmp_path / "something").write_text("already here")
    with pytest.raises(FileExistsError):
        write_dataset(tmp_path, make_dataset())


def test_write_dataset_writes_the_dataset_level_files(tmp_path, make_dataset):
    root = tmp_path / "ds"
    write_dataset(root, make_dataset())
    for name in ("dataset_description.json", "participants.tsv", "participants.json", "README.md"):
        assert (root / name).is_file()
    assert (root / "README.md").read_text(encoding="utf-8").startswith("# Synthetic EMG dataset\n")
