import pytest

from emg_bids_converter.core.validators import check_enum, schema_enum


def test_schema_enum_returns_allowed_values():
    assert schema_enum("RecordingType") == ("continuous", "epoched", "discontinuous")


def test_schema_enum_returns_none_without_enum():
    assert schema_enum("SamplingFrequency") is None


def test_schema_enum_rejects_unknown_field():
    with pytest.raises(KeyError):
        schema_enum("NotABidsField")


def test_check_enum_accepts_allowed_value():
    check_enum("RecordingType", "continuous")


def test_check_enum_rejects_other_value():
    with pytest.raises(ValueError, match="RecordingType"):
        check_enum("RecordingType", "streaming")


def test_check_enum_ignores_fields_without_enum():
    check_enum("SamplingFrequency", "anything")
