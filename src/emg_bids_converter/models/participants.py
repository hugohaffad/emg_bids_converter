from dataclasses import asdict, dataclass

from ..core.validators import check_row


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
        check_row(asdict(self), rule="modality_agnostic.Participants")