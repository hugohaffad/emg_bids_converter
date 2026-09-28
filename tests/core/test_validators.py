import pytest

from emg_bids_converter.core.validators import check_field, schema_enum


def test_schema_enum_returns_allowed_values():
    assert schema_enum("RecordingType") == ("continuous", "epoched", "discontinuous")


def test_schema_enum_returns_none_without_enum():
    assert schema_enum("SamplingFrequency") is None


def test_schema_enum_rejects_unknown_field():
    with pytest.raises(KeyError):
        schema_enum("NotABidsField")


def test_check_field_accepts_matching_type():
    check_field("x", 3.5)


def test_check_field_rejects_wrong_type():
    with pytest.raises(TypeError, match="x"):
        check_field("x", "not a number")


def test_check_field_accepts_allowed_enum_value():
    check_field("RecordingType", "continuous")


def test_check_field_rejects_other_enum_value():
    with pytest.raises(ValueError, match="RecordingType"):
        check_field("RecordingType", "streaming")


def test_check_field_accepts_value_at_minimum():
    check_field("EMGChannelCount", 0)


def test_check_field_rejects_value_below_minimum():
    with pytest.raises(ValueError, match="EMGChannelCount"):
        check_field("EMGChannelCount", -1)


def test_check_field_accepts_matching_pattern():
    check_field("participant_id", "sub-01")


def test_check_field_rejects_non_matching_pattern():
    with pytest.raises(ValueError, match="participant_id"):
        check_field("participant_id", "01")
