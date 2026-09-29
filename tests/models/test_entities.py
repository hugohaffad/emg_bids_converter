import pytest

from emg_bids_converter.models.entities import Entities


def test_entities_valid():
    Entities(subject="01", task="mvc", run="1")


def test_entities_task_cannot_be_none():
    with pytest.raises(ValueError, match="task"):
        Entities(subject="01", task=None)


def test_entities_rejects_prefixed_subject():
    with pytest.raises(ValueError, match="subject"):
        Entities(subject="sub-01", task="mvc")