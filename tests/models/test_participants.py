import pytest

from emg_bids_converter.models.participants import Participant


def test_participant_valid():
    Participant(participant_id="sub-01")


def test_participant_id_cannot_be_empty():
    with pytest.raises(ValueError, match="participant_id"):
        Participant(participant_id="")


def test_participant_id_must_match_pattern():
    with pytest.raises(ValueError, match="participant_id"):
        Participant(participant_id="01")


def test_participant_age_at_limit():
    Participant(participant_id="sub-01", age=89)


def test_participant_age_above_limit():
    with pytest.raises(ValueError, match="age"):
        Participant(participant_id="sub-01", age=90)
