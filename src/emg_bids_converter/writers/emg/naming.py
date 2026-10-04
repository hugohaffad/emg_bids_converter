"""Build BIDS paths and filenames from entities"""

from dataclasses import fields
from pathlib import Path

from ...core.schema import load
from ...models.emg.entities import Entities

_FILE_RULES = {
    "emg": ("emg", "emg"),
    "channels": ("channels", "channels__emg"),
    "electrodes": ("channels", "electrodes__emg"),
    "coordsystem": ("channels", "coordsystem__emg"),
}


def build_filename(entities: Entities, suffix: str, extension: str, space: str | None = None) -> str:
    """Build a BIDS filename, keeping only the entities the file's rule allows"""
    schema = load()
    group, rule = _FILE_RULES[suffix]
    allowed = schema.rules.files.raw[group][rule].entities
    if space is not None and "space" not in allowed:
        raise ValueError(f"space is not allowed for suffix {suffix!r}")

    values = {field.name: getattr(entities, field.name) for field in fields(entities)}
    values["space"] = space

    parts = [
        f"{schema.objects.entities[entity].name}-{values[entity]}"
        for entity in schema.rules.entities
        if entity in allowed and values.get(entity) is not None
    ]
    return "_".join(parts + [suffix]) + extension


def build_directory(root: Path, entities: Entities) -> Path:
    """Return root/sub-<label>/[ses-<label>/]emg"""
    directory = root / f"sub-{entities.subject}"
    if entities.session is not None:
        directory = directory / f"ses-{entities.session}"
    return directory / "emg"