"""Object level: a whole file (filename, TSV row, JSON) against the rules that apply to it."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Literal

from .fields import check_entity, check_field
from .rules import applicable, filename_rules, level, merged_fields, rule, single

_METADATA_GROUPS = ("sidecars", "json", "dataset_metadata")


@dataclass(frozen=True)
class Issue:
    """A problem found while checking a file against the BIDS schema."""
    level: Literal["error", "warning"]
    field: str | None
    message: str
    exception: type[Exception] = ValueError


def _field_issue(check: Callable, field: str, *args) -> Issue | None:
    """Run a field-level check and turn its exception, if any, into an error Issue."""
    try:
        check(field, *args)
    except (TypeError, ValueError) as error:
        return Issue("error", field, str(error), type(error))
    return None


def _raise_first_error(issues: list[Issue]) -> None:
    """Raise the exception of the first error, ignoring warnings."""
    for issue in issues:
        if issue.level == "error":
            raise issue.exception(issue.message)


def entities_issues(entities: Mapping[str, str | None], context: Mapping) -> list[Issue]:
    """Return the problems of filename entities against the filename rule of their file."""
    path = single(filename_rules(context), "filename", context)
    levels = rule(path).entities
    issues = [Issue("error", entity, f"{entity} is not allowed by rules.{path}")
              for entity in entities if entity not in levels]
    for entity, requirement in levels.items():
        value = entities.get(entity)
        if value is None:
            if level(requirement) == "required":
                issues.append(Issue("error", entity, f"{entity} is required by rules.{path}"))
            continue
        if issue := _field_issue(check_entity, entity, value):
            issues.append(issue)
    return issues


def check_entities(entities: Mapping[str, str | None], context: Mapping) -> None:
    """Raise if filename entities break the filename rule of their file."""
    _raise_first_error(entities_issues(entities, context))


def row_issues(row: Mapping, context: Mapping) -> list[Issue]:
    """Return the problems of a TSV row against the tabular rule of its file."""
    applied, _ = applicable(("tabular_data",), context)
    path = single(applied, "tabular", context)
    table = rule(path)
    index_columns = table.get("index_columns", ())
    issues = [Issue("error", column, f"{column} is not defined by rules.{path}")
              for column in row if column not in table.columns]
    for column, requirement in table.columns.items():
        value = row.get(column)
        if value is None:
            if level(requirement) == "required" and column in index_columns:
                issues.append(Issue("error", column, f"{column} identifies the row in rules.{path} and cannot be None"))
            continue
        if issue := _field_issue(check_field, column, value, "columns"):
            issues.append(issue)
    return issues


def check_row(row: Mapping, context: Mapping) -> None:
    """Raise if a TSV row breaks the tabular rule of its file."""
    _raise_first_error(row_issues(row, context))


def metadata_issues(data: Mapping, context: Mapping) -> list[Issue]:
    """Return the problems of JSON metadata against the rules that apply to its file."""
    content = {key: value for key, value in data.items() if value is not None}
    applied, _ = applicable(_METADATA_GROUPS, {**context, "json": content, "sidecar": content})
    if not applied:
        raise ValueError(f"no metadata rule applies to the file context {dict(context)}")
    fields = merged_fields(applied)
    issues = [Issue("error", field, f"{field} is not defined by the rules that apply to this file")
              for field in content if field not in fields]
    for field, (strength, path) in fields.items():
        value = content.get(field)
        if value is None:
            if strength == "required":
                issues.append(Issue("error", field, f"{field} is required by rules.{path}"))
            elif strength == "recommended":
                issues.append(Issue("warning", field, f"{field} is recommended by rules.{path}"))
            continue
        if issue := _field_issue(check_field, field, value, "metadata"):
            issues.append(issue)
    return issues


def check_metadata(data: Mapping, context: Mapping) -> None:
    """Raise if JSON metadata breaks the rules that apply to its file."""
    _raise_first_error(metadata_issues(data, context))
