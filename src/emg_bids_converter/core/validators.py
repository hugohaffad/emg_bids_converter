"""Checks against the BIDS schema."""

from collections.abc import Mapping
from dataclasses import fields

import jsonschema

from .schema import load


def _schema_object(key: str):
    """Return the schema definition of a BIDS field. Raises KeyError if the field is not defined in the schema."""
    schema = load()
    if key in schema.objects.columns:
        return schema.objects.columns[key]
    if key in schema.objects.metadata:
        return schema.objects.metadata[key]
    raise KeyError(f"{key!r} not found.")


def schema_enum(key: str) -> tuple[str, ...] | None:
    """Return the allowed values if they exist for a BIDS schema field, else None."""
    values = _schema_object(key).get("enum")
    return tuple(values) if values is not None else None


def _plain(obj):
    """Convert a Namespace into plain dicts/lists."""
    if isinstance(obj, Mapping):
        return {k: _plain(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_plain(v) for v in obj]
    return obj


def check_field(field: str, value) -> None:
    """Raise TypeError/ValueError if value violates the schema's declared constraints for that field."""
    spec = _plain(_schema_object(field))
    try:
        jsonschema.validate(instance=value, schema=spec)
    except jsonschema.ValidationError as e:
        exc = TypeError if e.validator == "type" else ValueError
        raise exc(f"invalid {field}={value!r}: {e.message}") from e


def check_dataclass(instance, required: tuple[str, ...] = ()) -> None:
    """Validate every field of a dataclass instance against the schema."""
    for field in fields(instance):
        value = getattr(instance, field.name)
        if field.name in required:
            if isinstance(value, str) and not value.strip():
                raise ValueError(f"{field.name} cannot be empty")
        elif value is None:
            continue
        check_field(field.name, value)
