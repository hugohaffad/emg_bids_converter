from dataclasses import dataclass
import numpy as np

from .channels import Channel
from .electrodes import Electrode
from .coordinate_systems import CoordinateSystem
from .sidecars import Sidecar


@dataclass(frozen=True, eq=False, repr=False)
class Recording:
    signal: np.ndarray
    channels: list[Channel]
    electrodes: list[Electrode]
    coordinate_systems: dict[str, CoordinateSystem]
    metadata: Sidecar

    def __post_init__(self) -> None:
        if self.signal.shape[0] != len(self.channels):
            raise ValueError(f"signal has {self.signal.shape[0]} rows but {len(self.channels)} channels")

        # rules.checks.emg.EMGChannelCountReq: EMGChannelCount must equal the number of channels with type "EMG"
        if self.metadata.EMGChannelCount is not None:
            emg_count = sum(1 for c in self.channels if c.type__channels == "EMG")
            if self.metadata.EMGChannelCount != emg_count:
                raise ValueError(
                    f"EMGChannelCount={self.metadata.EMGChannelCount} does not match "
                    f"{emg_count} channels of type EMG"
                )

        # (name, group) MUST be unique
        seen = set()
        for e in self.electrodes:
            key = (e.name__electrodes, e.group__emg)
            if key in seen:
                raise ValueError(f"duplicate electrode (name, group)={key!r}")
            seen.add(key)

        # objects.columns.reference__emg: must be "bipolar", "n/a", or an existing electrode name
        electrode_names = {e.name__electrodes for e in self.electrodes}
        for c in self.channels:
            ref = c.reference__emg
            if ref is not None and ref not in ("bipolar", "n/a") and ref not in electrode_names:
                raise ValueError(
                    f"channel {c.name__channels!r} reference={ref!r} "
                    f"is not 'bipolar', 'n/a', or a known electrode name"
                )

        # rules.checks.emg.EMGCoordSysMatch: electrodes.tsv.coordinate_system must reference a declared "space" label
        declared_spaces = set(self.coordinate_systems.keys())
        for e in self.electrodes:
            if e.coordinate_system is not None and e.coordinate_system not in declared_spaces:
                raise ValueError(
                    f"electrode {e.name__electrodes!r} coordinate_system="
                    f"{e.coordinate_system!r} is not among declared coordinate systems "
                    f"{sorted(declared_spaces)}"
                )

        # rules.checks.emg.EMGCoordSysParents: ParentCoordinateSystem must reference a declared "space" label
        for space, cs in self.coordinate_systems.items():
            if cs.ParentCoordinateSystem is not None and cs.ParentCoordinateSystem not in declared_spaces:
                raise ValueError(
                    f"coordinate system {space!r} has ParentCoordinateSystem="
                    f"{cs.ParentCoordinateSystem!r} which is not among declared coordinate "
                    f"systems {sorted(declared_spaces)}"
                )
