"""Readers of proprietary EMG formats; read() picks the reader from the file extension"""

from pathlib import Path
from typing import Any, Callable

from ..models.emg.recording import Recording
from . import otb4

READERS: dict[str, Callable[..., Recording]] = {".otb4": otb4.read}


def read(path: Path, **kwargs: Any) -> Recording:
    """Read a recording with the reader matching its extension"""
    path = Path(path)
    reader = READERS.get(path.suffix.lower())
    if reader is None:
        raise ValueError(f"unsupported file type {path.suffix!r} ({path.name}); supported: {sorted(READERS)}")
    return reader(path, **kwargs)
