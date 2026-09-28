from bidsschematools.types import Namespace

from emg_bids_converter.core.schema import load


def test_load_returns_namespace():
    assert isinstance(load(), Namespace)


def test_load_is_cached():
    assert load() is load()


def test_schema_supports_emg():
    assert "emg" in load().rules.modalities