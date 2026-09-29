import pytest

from emg_bids_converter.core import (
    Issue, check_entities, check_metadata, check_row, entities_issues, metadata_issues, row_issues,
)

_EMG_RECORDING = {"datatype": "emg", "suffix": "emg", "extension": ".bdf"}
_EMG_SIDECAR = _EMG_RECORDING
_EMG_CHANNELS = {"datatype": "emg", "suffix": "channels", "extension": ".tsv"}
_EMG_ELECTRODES = {"datatype": "emg", "suffix": "electrodes", "extension": ".tsv"}
_EMG_COORDSYSTEM = {"datatype": "emg", "suffix": "coordsystem", "extension": ".json"}
_PARTICIPANTS = {"path": "/participants.tsv", "extension": ".tsv"}
_MINIMAL = dict(EMGPlacementScheme="Measured", EMGReference="n/a", SamplingFrequency=2000.0,
                PowerLineFrequency=50.0, RecordingType="continuous", SoftwareFilters="n/a", TaskName="rest")


def test_check_entities_accepts_required_only():
    check_entities({"subject": "01", "task": "mvc"}, _EMG_RECORDING)


def test_check_entities_rejects_missing_required():
    with pytest.raises(ValueError, match="task is required"):
        check_entities({"subject": "01"}, _EMG_RECORDING)


def test_check_entities_rejects_entity_not_allowed_by_rule():
    with pytest.raises(ValueError, match="space"):
        check_entities({"subject": "01", "task": "mvc", "space": "grid"}, _EMG_RECORDING)


def test_check_entities_delegates_label_check():
    with pytest.raises(ValueError, match="task"):
        check_entities({"subject": "01", "task": "max_force"}, _EMG_RECORDING)


def test_check_entities_follows_the_file_context():
    check_entities({"subject": "01", "space": "grid"}, _EMG_COORDSYSTEM)


def test_check_row_accepts_required_only():
    check_row({"name__channels": "ch1", "type__channels": "EMG", "units": "mV"}, _EMG_CHANNELS)


def test_check_row_rejects_undefined_column():
    with pytest.raises(ValueError, match="gain"):
        check_row({"name__channels": "ch1", "type__channels": "EMG", "units": "mV", "gain": 1.0},
                  _EMG_CHANNELS)


def test_check_row_validates_values_as_columns():
    with pytest.raises(ValueError, match="None"):
        check_row({"name__channels": "ch1", "type__channels": "EMG", "units": "mV", "reference__emg": "n/a"},
                  _EMG_CHANNELS)


def test_check_row_rejects_missing_row_identifier():
    with pytest.raises(ValueError, match="name__channels identifies the row"):
        check_row({"type__channels": "EMG", "units": "mV"}, _EMG_CHANNELS)


def test_check_row_accepts_missing_value_in_required_column():
    check_row({"name__channels": "TRIG", "type__channels": "TRIG", "units": None}, _EMG_CHANNELS)


def test_check_row_reads_levels_written_as_objects():
    with pytest.raises(ValueError, match="participant_id identifies the row"):
        check_row({"age": 30}, _PARTICIPANTS)


def test_check_row_accepts_missing_value_in_optional_index_column():
    check_row({"name__electrodes": "e1", "x": 1.0, "y": 2.0, "group__emg": None}, _EMG_ELECTRODES)


def test_check_metadata_accepts_required_only():
    check_metadata(_MINIMAL, _EMG_SIDECAR)


def test_check_metadata_names_the_rule_of_a_missing_field():
    with pytest.raises(ValueError, match="EMGTaskInformation"):
        check_metadata({**_MINIMAL, "TaskName": None}, _EMG_SIDECAR)


def test_check_metadata_rejects_field_outside_the_rules():
    with pytest.raises(ValueError, match="EMGCoordinateUnits"):
        check_metadata({**_MINIMAL, "EMGCoordinateUnits": "mm"}, _EMG_SIDECAR)


def test_check_metadata_applies_conditional_rules():
    with pytest.raises(ValueError, match="EMGPlacementSchemeDescription is required"):
        check_metadata({**_MINIMAL, "EMGPlacementScheme": "Other"}, _EMG_SIDECAR)


def test_check_metadata_finds_rules_outside_the_emg_group():
    with pytest.raises(ValueError, match="EpochLength is required by rules.sidecars.electrophys"):
        check_metadata({**_MINIMAL, "RecordingType": "epoched"}, _EMG_SIDECAR)


def test_check_metadata_ignores_none_for_key_presence():
    context = {"datatype": "emg", "suffix": "coordsystem", "extension": ".json"}
    data = {"EMGCoordinateSystem": "Other", "EMGCoordinateUnits": "mm",
            "EMGCoordinateSystemDescription": "Grid-relative", "ParentCoordinateSystem": None}
    check_metadata(data, context)


def test_check_metadata_rejects_unknown_file_context():
    with pytest.raises(ValueError, match="no metadata rule"):
        check_metadata(_MINIMAL, {"datatype": "emg", "suffix": "nonsense"})


def test_check_entities_rejects_unknown_file_context():
    with pytest.raises(ValueError, match="no filename rule"):
        check_entities({"subject": "01"}, {"datatype": "emg", "suffix": "nonsense", "extension": ".tsv"})


def test_check_row_rejects_unknown_file_context():
    with pytest.raises(ValueError, match="no tabular rule"):
        check_row({"name__channels": "ch1"}, {"datatype": "emg", "suffix": "nonsense", "extension": ".tsv"})


# --- Issues ---


def test_metadata_issues_reports_every_problem_at_once():
    data = {**_MINIMAL, "SamplingFrequency": "fast", "RecordingType": "streaming", "TaskName": None}
    fields = {issue.field for issue in metadata_issues(data, _EMG_SIDECAR) if issue.level == "error"}
    assert fields == {"SamplingFrequency", "RecordingType", "TaskName"}


def test_metadata_issues_warns_about_missing_recommended_fields():
    warnings = {issue.field for issue in metadata_issues(_MINIMAL, _EMG_SIDECAR) if issue.level == "warning"}
    assert {"EMGChannelCount", "HardwareFilters", "Manufacturer"} <= warnings


def test_metadata_issues_keeps_the_exception_type():
    [issue] = [i for i in metadata_issues({**_MINIMAL, "SamplingFrequency": "fast"}, _EMG_SIDECAR) if i.level == "error"]
    assert issue == Issue("error", "SamplingFrequency", issue.message, TypeError)


def test_check_metadata_ignores_warnings():
    check_metadata(_MINIMAL, _EMG_SIDECAR)


def test_check_metadata_does_not_enforce_undetermined_rules():
    check_metadata({"Name": "x", "BIDSVersion": "1.11.1"}, {"path": "/dataset_description.json", "extension": ".json"})


def test_row_issues_reports_every_problem_at_once():
    row = {"name__channels": None, "type__channels": "emg", "units": "mV", "status": "ok"}
    assert {issue.field for issue in row_issues(row, _EMG_CHANNELS)} == {"name__channels", "type__channels", "status"}


def test_entities_issues_reports_every_problem_at_once():
    entities = {"subject": "sub-01", "task": None, "space": "grid"}
    assert {issue.field for issue in entities_issues(entities, _EMG_RECORDING)} == {"subject", "task", "space"}
