import jsonschema
import numpy as np
import pytest

from emg_bids_converter.core.schema import load
from emg_bids_converter.core.validation.fields import (
    _check_python, _format_checker, _from_definition, _spec, check_entity, check_field,
)


def test_spec_returns_column_definition():
    assert _spec("x", "columns")["type"] == "number"


def test_spec_returns_metadata_definition():
    assert _spec("SamplingFrequency", "metadata")["type"] == "number"


def test_spec_distinguishes_sections_for_shared_names():
    assert _spec("HED", "columns") != _spec("HED", "metadata")


def test_spec_rejects_field_from_wrong_section():
    with pytest.raises(KeyError, match="columns"):
        _spec("SamplingFrequency", "columns")


def test_from_definition_translates_format_to_type():
    assert _from_definition({"Format": "string"}) == {"type": "string"}


def test_from_definition_translates_maximum():
    assert _from_definition(_spec("age", "columns")["definition"]) == {"type": "number", "maximum": 89}


def test_from_definition_translates_levels_to_enum():
    spec = _from_definition(_spec("handedness", "columns")["definition"])
    assert "L" in spec["enum"] and "Left-handed" not in spec["enum"]


def test_from_definition_does_not_mutate_cached_spec():
    before = _spec("age", "columns")
    _from_definition(before["definition"])
    assert _spec("age", "columns") == before and "definition" in before


def _validate(value, spec):
    jsonschema.validate(value, spec, format_checker=_format_checker())


def test_format_checker_registers_exactly_the_bids_formats():
    assert set(_format_checker().checkers) == set(load().objects.formats.keys())


def test_format_checker_accepts_valid_rrid():
    _validate("RRID:SCR_002823", _spec("strain_rrid", "columns"))


def test_format_checker_rejects_rrid_without_prefix():
    with pytest.raises(jsonschema.ValidationError):
        _validate("SCR_002823", _spec("strain_rrid", "columns"))


def test_format_checker_rejects_malformed_hed_version():
    with pytest.raises(jsonschema.ValidationError):
        _validate("v8", _spec("HEDVersion", "metadata"))


def test_format_checker_ignores_non_strings():
    _validate(3, {"format": "rrid"})


def test_check_python_rejects_numpy_scalar():
    with pytest.raises(TypeError, match="float32"):
        _check_python("SamplingFrequency", np.float32(2000), "metadata")


def test_check_python_rejects_numpy_float64_despite_float_inheritance():
    with pytest.raises(TypeError, match="float64"):
        _check_python("x", np.float64(1.0), "columns")


def test_check_python_rejects_nan():
    with pytest.raises(ValueError, match="finite"):
        _check_python("SamplingFrequency", float("nan"), "metadata")


def test_check_python_rejects_nested_nan():
    with pytest.raises(ValueError, match="AnchorCoordinates"):
        _check_python("AnchorCoordinates", [0.0, float("inf")], "metadata")


def test_check_python_rejects_na_string_in_columns():
    with pytest.raises(ValueError, match="None"):
        _check_python("reference__emg", "n/a", "columns")


def test_check_python_accepts_na_string_in_metadata():
    _check_python("PowerLineFrequency", "n/a", "metadata")


def test_check_python_rejects_tab_in_columns():
    with pytest.raises(ValueError, match="TSV"):
        _check_python("description", "a\tb", "columns")


def test_check_python_accepts_newline_in_metadata():
    _check_python("Instructions", "line 1\nline 2", "metadata")


def test_check_python_rejects_empty_string_in_columns():
    with pytest.raises(ValueError, match="None"):
        _check_python("description", "", "columns")


def test_check_field_accepts_valid_value():
    check_field("x", 3.5, "columns")


def test_check_field_rejects_wrong_type():
    with pytest.raises(TypeError, match="x"):
        check_field("x", "not a number", "columns")


def test_check_field_rejects_value_outside_enum():
    with pytest.raises(ValueError, match="RecordingType"):
        check_field("RecordingType", "streaming", "metadata")


def test_check_field_applies_definition():
    with pytest.raises(ValueError, match="age"):
        check_field("age", 90, "columns")


def test_check_field_applies_formats():
    with pytest.raises(ValueError, match="strain_rrid"):
        check_field("strain_rrid", "SCR_002823", "columns")


def test_check_field_runs_python_checks_first():
    with pytest.raises(TypeError, match="float32"):
        check_field("SamplingFrequency", np.float32(2000), "metadata")


def test_check_field_reports_precise_error_inside_any_of():
    with pytest.raises(ValueError, match="minimum"):
        check_field("PowerLineFrequency", -50, "metadata")


def test_check_field_accepts_enumerated_na_in_metadata():
    check_field("PowerLineFrequency", "n/a", "metadata")


def test_check_field_rejects_field_from_wrong_section():
    with pytest.raises(KeyError):
        check_field("SamplingFrequency", 2000.0, "columns")


def test_check_entity_accepts_valid_label():
    check_entity("subject", "01")


def test_check_entity_accepts_plus_in_label():
    check_entity("acquisition", "pilot+1")


def test_check_entity_rejects_prefixed_label():
    with pytest.raises(ValueError, match="subject"):
        check_entity("subject", "sub-01")


def test_check_entity_rejects_underscore():
    with pytest.raises(ValueError, match="task"):
        check_entity("task", "max_force")


def test_check_entity_applies_index_format_to_run():
    with pytest.raises(ValueError, match="run"):
        check_entity("run", "a1")


def test_check_entity_rejects_non_string():
    with pytest.raises(TypeError, match="run"):
        check_entity("run", 1)


def test_check_entity_rejects_short_entity_name():
    with pytest.raises(KeyError, match="entities"):
        check_entity("sub", "01")


def test_check_python_rejects_blank_string_in_metadata():
    with pytest.raises(ValueError, match="None"):
        _check_python("TaskName", "  ", "metadata")
