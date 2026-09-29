from dataclasses import asdict, dataclass

from ...core import check_row

_CONTEXT = {"datatype": "emg", "suffix": "channels", "extension": ".tsv"}


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
        check_row(asdict(self), _CONTEXT)
