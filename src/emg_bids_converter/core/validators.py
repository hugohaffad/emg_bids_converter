"""Checks against the BIDS schema."""

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


def check_enum(field: str, value: str) -> None:
    """Raise ValueError if value isn't among the schema's allowed values for that field, if any."""
    allowed = schema_enum(field)
    if allowed is not None and value not in allowed:
        raise ValueError(f"invalid {field}={value!r}; expected one of: {', '.join(allowed)}")
