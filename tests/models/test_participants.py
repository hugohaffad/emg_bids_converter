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

def test_participant_id_cannot_be_none():
    with pytest.raises(ValueError, match="participant_id"):
        Participant(participant_id=None)


def test_participant_sex_must_be_a_level():
    with pytest.raises(ValueError, match="sex"):
        Participant(participant_id="sub-01", sex="banana")


def test_participant_handedness_accepts_short_level():
    Participant(participant_id="sub-01", handedness="R")


def test_participant_strain_rrid_must_have_prefix():
    with pytest.raises(ValueError, match="strain_rrid"):
        Participant(participant_id="sub-01", strain_rrid="IMSR_JAX:000664")


def test_participant_species_is_a_string():
    with pytest.raises(TypeError, match="species"):
        Participant(participant_id="sub-01", species=9606.0)
