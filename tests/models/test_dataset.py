import pytest

from emg_bids_converter.models.dataset import Dataset
from emg_bids_converter.models.emg.entities import Entities
from emg_bids_converter.models.participants import Participant


def test_dataset_valid(make_dataset):
    make_dataset(subjects=("01", "02"))


def test_dataset_needs_a_recording(make_dataset):
    dataset = make_dataset()
    with pytest.raises(ValueError, match="at least one recording"):
        Dataset(description=dataset.description, participants=dataset.participants, recordings=[])


def test_dataset_participant_ids_are_unique(make_dataset):
    dataset = make_dataset()
    with pytest.raises(ValueError, match="duplicate participant_id"):
        Dataset(
            description=dataset.description,
            participants=dataset.participants * 2,
            recordings=dataset.recordings,
        )


def test_dataset_recordings_have_distinct_entities(make_dataset):
    dataset = make_dataset()
    with pytest.raises(ValueError, match="share the entities"):
        Dataset(
            description=dataset.description,
            participants=dataset.participants,
            recordings=dataset.recordings * 2,
        )


def test_dataset_participants_match_subjects(make_dataset, make_recording):
    dataset = make_dataset()
    # a recording for sub-02, who has no row in participants.tsv
    with pytest.raises(ValueError, match="does not match the subjects"):
        Dataset(
            description=dataset.description,
            participants=dataset.participants,
            recordings=dataset.recordings + [(Entities(subject="02", task="mvc"), make_recording())],
        )
    # a row in participants.tsv for sub-02, who has no recording
    with pytest.raises(ValueError, match="does not match the subjects"):
        Dataset(
            description=dataset.description,
            participants=dataset.participants + [Participant(participant_id="sub-02")],
            recordings=dataset.recordings,
        )
