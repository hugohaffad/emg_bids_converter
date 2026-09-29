"""Field level: one value against its definition in schema.objects."""

import math
import re
from functools import cache
from typing import Literal

from jsonschema import FormatChecker
from jsonschema.exceptions import best_match
from jsonschema.protocols import Validator
from jsonschema.validators import validator_for

from ..schema import load

Section = Literal["columns", "metadata"]


@cache
def _spec(field: str, section: Section) -> dict:
    """Return the schema definition of a BIDS field as a plain dict (cached)."""
    objects = load().objects[section]
    if field not in objects:
        raise KeyError(f"{field!r} not found in schema objects.{section}")
    return objects[field].to_dict()


def _from_definition(definition: dict) -> dict:
    """Translate a column `definition` block into JSON Schema."""
    spec = {"type": definition["Format"]}
    if "Maximum" in definition:
        spec["maximum"] = definition["Maximum"]
    if "Levels" in definition:
        spec["enum"] = list(definition["Levels"])
    return spec


def _matcher(pattern: str):
    """Return a function telling whether a value fully matches pattern (non-strings pass)."""
    def match(value) -> bool:
        return not isinstance(value, str) or re.fullmatch(pattern, value) is not None
    return match


@cache
def _format_checker() -> FormatChecker:
    """Build a FormatChecker from the regex patterns declared in schema.objects.formats."""
    checker = FormatChecker(formats=())
    for name, fmt in load().objects.formats.items():
        checker.checks(name)(_matcher(fmt.pattern))
    return checker


def _check_python(field: str, value, section: Section) -> None:
    """Raise TypeError/ValueError for values a JSON or TSV file cannot faithfully hold."""
    if type(value) not in (str, int, float, bool, list, dict):
        raise TypeError(f"invalid {field}={value!r}: {type(value).__name__} is not a native Python type")
    if type(value) is float and not math.isfinite(value):
        raise ValueError(f"invalid {field}={value!r}: must be a finite number")
    if type(value) is str and not value.strip():
        raise ValueError(f"invalid {field}={value!r}: use None for missing values")
    if type(value) is str and section == "columns":
        if value == "n/a":
            raise ValueError(f"invalid {field}={value!r}: use None for missing values")
        if any(char in value for char in "\t\n\r"):
            raise ValueError(f"invalid {field}={value!r}: tabs and line breaks are not supported in TSV cells")
    if type(value) is list:
        for item in value:
            _check_python(field, item, section)
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise TypeError(f"invalid {field}: key {key!r} must be a string")
            _check_python(field, item, section)


@cache
def _validator(field: str, section: Section) -> Validator:
    """Build, once per field, the validator enforcing its schema constraints."""
    spec = _spec(field, section)
    if "definition" in spec:
        spec = _from_definition(spec["definition"])
    return validator_for(spec)(spec, format_checker=_format_checker())


def check_field(field: str, value, section: Section) -> None:
    """Raise TypeError/ValueError if value cannot be written as this BIDS field."""
    _check_python(field, value, section)
    error = best_match(_validator(field, section).iter_errors(value))
    if error is not None:
        exc = TypeError if error.validator == "type" else ValueError
        raise exc(f"invalid {field}={value!r}: {error.message}")


@cache
def _entity_pattern(entity: str) -> re.Pattern:
    """Compile, once per entity, the regex its label must fully match."""
    entities = load().objects.entities
    if entity not in entities:
        raise KeyError(f"{entity!r} not found in schema objects.entities")
    return re.compile(load().objects.formats[entities[entity].format].pattern)


def check_entity(entity: str, value) -> None:
    """Raise TypeError/ValueError if value is not a valid label for this BIDS entity."""
    if type(value) is not str:
        raise TypeError(f"invalid {entity}={value!r}: must be a string")
    pattern = _entity_pattern(entity)
    if pattern.fullmatch(value) is None:
        raise ValueError(f"invalid {entity}={value!r}: must match {pattern.pattern}")
