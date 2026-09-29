import pytest

from emg_bids_converter.core.validation.expressions import Undetermined, evaluate, parse_selector
from emg_bids_converter.core.validation.rules import rule, rule_paths


def _eval(selector, **context):
    return evaluate(parse_selector(selector), context)


def test_evaluate_compares_identifiers():
    assert _eval('datatype == "emg"', datatype="emg")


def test_evaluate_missing_property_is_none():
    assert not _eval("sidecar.RecordingType == 'epoched'", sidecar={})


def test_evaluate_key_membership():
    assert _eval('"ParentCoordinateSystem" in json', json={"ParentCoordinateSystem": "hand"})
    assert not _eval('"ParentCoordinateSystem" in json', json={})


def test_evaluate_intersects():
    assert _eval("intersects([datatype], ['emg'])", datatype="emg")


def test_evaluate_missing_dataset_is_not_derivative():
    assert not _eval('dataset.dataset_description.DatasetType == "derivative"')


def test_evaluate_refuses_what_it_cannot_know():
    with pytest.raises(Undetermined):
        _eval('!exists("CITATION.cff", "dataset")')


def test_every_selector_parses():
    for group in ("sidecars", "json", "dataset_metadata", "tabular_data"):
        for path in rule_paths(group):
            for selector in rule(path).selectors:
                parse_selector(selector)


def test_evaluate_literals():
    assert _eval("true") is True
    assert _eval("false") is False
    assert _eval("null") is None
    assert _eval("sidecar.Missing == null", sidecar={})


def test_evaluate_refuses_unknown_unary_operator():
    from bidsschematools.expressions import parse

    node = parse("!x")  # a fresh tree: parse_selector's cached one must not be mutated
    node.op = "~"
    with pytest.raises(Undetermined):
        evaluate(node, {"x": True})
