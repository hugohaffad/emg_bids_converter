from emg_bids_converter.models.emg.channels import Channel
from emg_bids_converter.models.emg.electrodes import Electrode
from emg_bids_converter.writers._tsv import select_columns, write_tsv


def _lines(path):
    return path.read_text(encoding="utf-8").splitlines()


def test_header_uses_bids_column_names(tmp_path):
    path = tmp_path / "channels.tsv"
    write_tsv([Channel(name__channels="ch1", type__channels="EMG", units="mV")], path)
    assert _lines(path) == ["name\ttype\tunits", "ch1\tEMG\tmV"]


def test_none_is_written_as_na_when_the_column_has_a_value(tmp_path):
    path = tmp_path / "channels.tsv"
    rows = [
        Channel(name__channels="ch1", type__channels="EMG", units="mV", low_cutoff=10.0),
        Channel(name__channels="ch2", type__channels="EMG", units="mV"),
    ]
    write_tsv(rows, path)
    assert _lines(path) == ["name\ttype\tunits\tlow_cutoff", "ch1\tEMG\tmV\t10.0", "ch2\tEMG\tmV\tn/a"]


def test_empty_columns_are_dropped_unless_kept():
    rows = [Electrode(name__electrodes="e1", x=1.0, y=2.0)]
    assert select_columns(rows) == ["name__electrodes", "x", "y"]
    assert select_columns(rows, keep=("z",)) == ["name__electrodes", "x", "y", "z"]


def test_file_ends_with_a_newline(tmp_path):
    path = tmp_path / "channels.tsv"
    write_tsv([Channel(name__channels="ch1", type__channels="EMG", units="mV")], path)
    assert path.read_text(encoding="utf-8").endswith("\n")
