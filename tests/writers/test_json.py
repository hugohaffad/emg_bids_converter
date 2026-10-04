import json

import numpy as np

from emg_bids_converter.models.dataset_description import DatasetDescription
from emg_bids_converter.writers._json import write_json, write_mapping


def test_none_fields_are_left_out(tmp_path):
    path = tmp_path / "dataset_description.json"
    write_json(DatasetDescription(Name="my dataset", BIDSVersion="1.11.1"), path)
    assert json.loads(path.read_text(encoding="utf-8")) == {"Name": "my dataset", "BIDSVersion": "1.11.1"}


def test_numpy_values_are_written_as_python_values(tmp_path):
    path = tmp_path / "data.json"
    write_mapping({"SamplingFrequency": np.float32(2000.0), "Anchor": np.array([1, 2])}, path)
    assert json.loads(path.read_text(encoding="utf-8")) == {"SamplingFrequency": 2000.0, "Anchor": [1, 2]}


def test_non_ascii_is_kept(tmp_path):
    path = tmp_path / "dataset_description.json"
    write_json(DatasetDescription(Name="Université de Toulouse", BIDSVersion="1.11.1"), path)
    assert "Université" in path.read_text(encoding="utf-8")
