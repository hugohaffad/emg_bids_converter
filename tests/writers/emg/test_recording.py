from emg_bids_converter.models.emg.coordinate_systems import CoordinateSystem
from emg_bids_converter.models.emg.electrodes import Electrode
from emg_bids_converter.models.emg.entities import Entities
from emg_bids_converter.writers.emg.recording import write_recording


def test_writes_signal_sidecar_and_channels(tmp_path, make_recording):
    written = write_recording(tmp_path, Entities(subject="01", task="mvc"), make_recording())
    assert sorted(p.name for p in written) == [
        "sub-01_task-mvc_channels.tsv",
        "sub-01_task-mvc_emg.bdf",
        "sub-01_task-mvc_emg.json",
    ]
    assert all(p.parent == tmp_path / "sub-01" / "emg" for p in written)


def test_writes_electrodes_and_one_coordsystem_per_space(tmp_path, make_recording):
    recording = make_recording(
        electrodes=[Electrode(name__electrodes="e1", x=0.0, y=0.0, coordinate_system="grid1")],
        coordinate_systems={
            "grid1": CoordinateSystem(
                EMGCoordinateSystem="Other",
                EMGCoordinateUnits="mm",
                EMGCoordinateSystemDescription="Grid-relative positions",
            )
        },
    )
    written = write_recording(tmp_path, Entities(subject="01", task="mvc"), recording)
    names = [p.name for p in written]
    assert any(n.endswith("_electrodes.tsv") and "space-" not in n for n in names)
    assert any(n.endswith("_space-grid1_coordsystem.json") for n in names)
