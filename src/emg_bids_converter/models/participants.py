from dataclasses import dataclass


@dataclass(frozen=True)
class Participant:
    """Class implementing the fields of the participants.tsv file (one row)"""
    participant_id: str
    species: str | float | None = None
    age: float | None = None
    sex: str | None = None
    handedness: str | None = None
    strain: str | float | None = None
    strain_rrid: str | None = None
    HED: str | None = None
