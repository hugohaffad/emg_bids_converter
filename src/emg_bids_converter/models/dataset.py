from collections import Counter
from dataclasses import dataclass

from .dataset_description import DatasetDescription
from .emg.entities import Entities
from .emg.recording import Recording
from .participants import Participant


@dataclass(frozen=True, eq=False, repr=False)
class Dataset:
    """A whole BIDS dataset: its description, its participants and its recordings."""
    description: DatasetDescription
    participants: list[Participant]
    recordings: list[tuple[Entities, Recording]]

    def __post_init__(self) -> None:
        if not self.recordings:
            raise ValueError("a dataset needs at least one recording")

        # participants.tsv: one row per participant (index column participant_id)
        ids = Counter(p.participant_id for p in self.participants)
        duplicates = sorted(i for i, n in ids.items() if n > 1)
        if duplicates:
            raise ValueError(f"duplicate participant_id {duplicates}")

        # Two recordings with the same entities would be written to the same files
        entities = Counter(e for e, _ in self.recordings)
        duplicates = [e for e, n in entities.items() if n > 1]
        if duplicates:
            raise ValueError(f"several recordings share the entities {duplicates}")

        # rules.checks.dataset.ParticipantIDMismatch: participant_id values in participants.tsv
        # must match the sub-<label> directories of the dataset
        subjects = {f"sub-{e.subject}" for e, _ in self.recordings}
        if set(ids) != subjects:
            raise ValueError(
                f"participant_id {sorted(set(ids))} does not match the subjects "
                f"of the recordings {sorted(subjects)}"
            )
