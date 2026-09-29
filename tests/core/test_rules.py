from emg_bids_converter.core.validation.rules import applicable, filename_rules, rule_paths

_EMG_SIDECAR = {"datatype": "emg", "suffix": "emg", "extension": ".bdf"}
_EMG_BASE = {"sidecars.emg.EMGRequired", "sidecars.emg.EMGRecommended", "sidecars.emg.EMGOptional",
             "sidecars.emg.EMGHardware", "sidecars.emg.EMGTaskInformation",
             "sidecars.emg.EMGInstitutionInformation"}


def test_rule_paths_reach_nested_rules():
    assert "json.emg.EMGChildCoordSystem" in rule_paths("json")


def test_applicable_selects_the_emg_sidecar_rules():
    sidecar = {"RecordingType": "continuous", "EMGPlacementScheme": "Measured"}
    applied, undetermined = applicable(("sidecars",), _EMG_SIDECAR | {"sidecar": sidecar})
    assert set(applied) == _EMG_BASE and not undetermined


def test_applicable_activates_conditional_rules():
    sidecar = {"RecordingType": "epoched", "EMGPlacementScheme": "Other"}
    applied, _ = applicable(("sidecars",), _EMG_SIDECAR | {"sidecar": sidecar})
    assert set(applied) == _EMG_BASE | {"sidecars.electrophys.EpochLengthRequired",
                                        "sidecars.emg.EMGPlacementSchemeDescription"}


def test_applicable_selects_the_child_coordsystem_rules():
    context = {"datatype": "emg", "suffix": "coordsystem", "extension": ".json",
               "json": {"EMGCoordinateSystem": "Other", "ParentCoordinateSystem": "hand"}}
    applied, _ = applicable(("json",), context)
    assert set(applied) == {"json.emg.EMGCoordsystemPositions", "json.emg.EMGCoordsystemOther",
                            "json.emg.EMGChildCoordSystem"}


def test_applicable_reports_undetermined_rules():
    context = {"path": "/dataset_description.json", "extension": ".json", "json": {"DatasetType": "raw"}}
    applied, undetermined = applicable(("dataset_metadata",), context)
    assert applied == ("dataset_metadata.dataset_description",)
    assert set(undetermined) == {"dataset_metadata.dataset_authors",
                                 "dataset_metadata.dataset_description_with_genetics"}


def test_each_emg_file_has_a_single_filename_rule():
    for suffix, extension in (("emg", ".bdf"), ("channels", ".tsv"), ("electrodes", ".tsv"), ("coordsystem", ".json")):
        assert len(filename_rules({"datatype": "emg", "suffix": suffix, "extension": extension})) == 1


def test_applicable_cache_distinguishes_booleans_from_numbers():
    from emg_bids_converter.core.validation.rules import _freeze, _thaw

    assert _freeze({"x": True}) != _freeze({"x": 1})
    assert _freeze({"x": 1}) != _freeze({"x": 1.0})
    context = {"datatype": "emg", "json": {"a": [1, {"b": True}], "c": None}}
    assert _thaw(_freeze(context)) == context
