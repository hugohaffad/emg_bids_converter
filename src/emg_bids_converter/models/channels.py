from dataclasses import dataclass, fields

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
        for field in fields(self):
            value = getattr(self, field.name)
            if field.name in ("name__channels", "type__channels", "units"):
                if not value.strip():
                    raise ValueError(f"{field.name} cannot be empty")
            elif value is None:
                continue
            check_field(field.name, value)
