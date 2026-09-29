from dataclasses import asdict, dataclass

from ..core import check_row

_CONTEXT = {"path": "/participants.tsv", "extension": ".tsv"}


@dataclass(frozen=True)
class Participant:
    """Class implementing the fields of the participants.tsv file (one row)"""
    participant_id: str
    species: str | None = None
    age: float | None = None
    sex: str | None = None
    handedness: str | None = None
    strain: str | None = None
    strain_rrid: str | None = None
    HED: str | None = None

    def __post_init__(self) -> None:
        check_row(asdict(self), _CONTEXT)