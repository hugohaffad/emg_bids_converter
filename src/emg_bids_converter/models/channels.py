from dataclasses import dataclass

from ..core.validators import check_field


@dataclass(frozen=True)
class Channel:
    """Class implementing the fields of the *_channels.tsv file (one row)"""
    name__channels: str
    type__channels: str
    units: str
    description: str | None = None
    sampling_frequency: float | None = None
    signal_electrode: str | None = None
    reference__emg: str | None = None
    group__emg: float | str | None = None
    target_muscle: str | None = None
    placement_scheme: str | None = None
    placement_description: str | None = None
    interelectrode_distance: float | None = None
    low_cutoff: float | None = None
    high_cutoff: float | None = None
    notch: str | None = None
    status: str | None = None
    status_description: str | None = None

    def __post_init__(self) -> None:
        if not self.name__channels.strip():
            raise ValueError("name cannot be empty")
        if not self.type__channels.strip():
            raise ValueError("type cannot be empty")
        if not self.units.strip():
            raise ValueError("units cannot be empty")

        check_field("type__channels", self.type__channels)
        for field in ("placement_scheme", "status", "group__emg", "sampling_frequency",
                      "interelectrode_distance", "low_cutoff", "high_cutoff"):
            value = getattr(self, field)
            if value is not None:
                check_field(field, value)
