from pathlib import Path

import pytest

from emg_bids_converter.models.emg.entities import Entities
from emg_bids_converter.writers.emg.naming import build_directory, build_filename


def test_entities_are_written_in_schema_order():
    entities = Entities(subject="01", task="mvc", session="pre", run="1")
    assert build_filename(entities, "emg", ".bdf") == "sub-01_ses-pre_task-mvc_run-1_emg.bdf"


def test_optional_entities_left_unset_are_omitted():
    assert build_filename(Entities(subject="01", task="mvc"), "channels", ".tsv") == "sub-01_task-mvc_channels.tsv"


def test_space_is_allowed_for_coordsystem_only():
    entities = Entities(subject="01", task="mvc")
    assert "_space-grid1_" in build_filename(entities, "coordsystem", ".json", space="grid1")
    # rules.files.raw.channels.electrodes__emg has no space entity
    with pytest.raises(ValueError, match="space"):
        build_filename(entities, "electrodes", ".tsv", space="grid1")


def test_directory_with_and_without_session():
    root = Path("ds")
    assert build_directory(root, Entities(subject="01", task="mvc")) == root / "sub-01" / "emg"
    assert build_directory(root, Entities(subject="01", task="mvc", session="pre")) == root / "sub-01" / "ses-pre" / "emg"
