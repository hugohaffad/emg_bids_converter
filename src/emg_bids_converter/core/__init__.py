"""The BIDS schema and the checks built on it.

Everything enforced here is read from the schema: field definitions (schema.objects),
label formats (schema.objects.formats) and the rules saying which fields a file needs
(schema.rules). Models never name the rules they follow: they describe their file with a
context (datatype, suffix, extension, or path) and the schema says which rules apply.

- schema: loading the BIDS schema, once.
- validation.fields: one value against its definition.
- validation.expressions: schema selectors evaluated against a file context.
- validation.rules: navigating schema.rules and selecting the rules that apply to a file.
- validation.objects: a whole file (filename, TSV row, JSON) against those rules.
"""

from .validation.fields import check_entity, check_field
from .validation.objects import (
    Issue,
    check_entities,
    check_metadata,
    check_row,
    entities_issues,
    metadata_issues,
    row_issues,
)

__all__ = [
    "Issue",
    "check_entities",
    "check_entity",
    "check_field",
    "check_metadata",
    "check_row",
    "entities_issues",
    "metadata_issues",
    "row_issues",
]
