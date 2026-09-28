from dataclasses import dataclass

from ..core.validators import check_dataclass


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

    def __post_init__(self) -> None:
        check_dataclass(self, required=("participant_id",))

        if self.age is not None and self.age > 89:
            raise ValueError(f"age={self.age!r} must not exceed 89")
