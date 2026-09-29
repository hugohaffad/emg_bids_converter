from dataclasses import asdict, dataclass

from ..core.validators import check_entities


@dataclass(frozen=True)
class Entities:
    """BIDS filename entities identifying one EMG recording"""
    subject: str
    task: str
    session: str | None = None
    acquisition: str | None = None
    run: str | None = None
    recording: str | None = None

    def __post_init__(self) -> None:
        check_entities(asdict(self), rule="emg.emg")