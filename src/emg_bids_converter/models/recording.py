from dataclasses import dataclass
import numpy as np

from .channels import Channel
from .electrodes import Electrode
from .coordinate_systems import CoordinateSystem
from .sidecars import Sidecar


@dataclass(frozen=True, eq=False, repr=False)
class Recording:
    """One EMG recording: its signal and every file describing it."""
    signal: np.ndarray
    channels: list[Channel]
    electrodes: list[Electrode]
    coordinate_systems: dict[str, CoordinateSystem]
    metadata: Sidecar

    def __post_init__(self) -> None:
        # Signal convention: (n_channels, n_samples), one row per channels.tsv row
        if self.signal.ndim != 2:
            raise ValueError(f"signal must be 2-D (n_channels, n_samples), got {self.signal.ndim}-D")
        if self.signal.shape[0] != len(self.channels):
            raise ValueError(f"signal has {self.signal.shape[0]} rows but {len(self.channels)} channels")

        # rules.tabular_data.emg.EMGChannels: index_columns [name]
        seen_channels = set()
        for c in self.channels:
            if c.name__channels in seen_channels:
                raise ValueError(f"duplicate channel name {c.name__channels!r}")
            seen_channels.add(c.name__channels)

        # rules.tabular_data.emg.EMGElectrodes: index_columns [name, group]
        seen_electrodes = set()
        for e in self.electrodes:
            key = (e.name__electrodes, e.group__emg)
            if key in seen_electrodes:
                raise ValueError(f"duplicate electrode (name, group)={key!r}")
            seen_electrodes.add(key)

        # rules.checks.emg.EMGChannelCountReq: EMGChannelCount must equal the number of channels with type "EMG"
        if self.metadata.EMGChannelCount is not None:
            emg_count = sum(1 for c in self.channels if c.type__channels == "EMG")
            if self.metadata.EMGChannelCount != emg_count:
                raise ValueError(
                    f"EMGChannelCount={self.metadata.EMGChannelCount} does not match "
                    f"{emg_count} channels of type EMG"
                )

        # objects.columns.reference__emg: "bipolar" or the name of an electrode in electrodes.tsv
        electrode_names = {e.name__electrodes for e in self.electrodes}
        for c in self.channels:
            ref = c.reference__emg
            if ref is not None and ref != "bipolar" and ref not in electrode_names:
                raise ValueError(
                    f"channel {c.name__channels!r} reference={ref!r} "
                    f"is neither 'bipolar' nor a known electrode name"
                )

        # rules.checks.emg.EMGCoordSysMatch: electrodes.tsv coordinate_system must be a declared space label
        declared_spaces = set(self.coordinate_systems)
        for e in self.electrodes:
            if e.coordinate_system is not None and e.coordinate_system not in declared_spaces:
                raise ValueError(
                    f"electrode {e.name__electrodes!r} coordinate_system={e.coordinate_system!r} "
                    f"is not among declared coordinate systems {sorted(declared_spaces)}"
                )

        # rules.checks.emg.EMGCoordSysParents: ParentCoordinateSystem must be a declared space label
        for space, cs in self.coordinate_systems.items():
            if cs.ParentCoordinateSystem is not None and cs.ParentCoordinateSystem not in declared_spaces:
                raise ValueError(
                    f"coordinate system {space!r} has ParentCoordinateSystem={cs.ParentCoordinateSystem!r}, "
                    f"which is not among declared coordinate systems {sorted(declared_spaces)}"
                )
