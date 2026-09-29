"""Rule access: navigating schema.rules and selecting the rules that apply to a file."""

from collections.abc import Mapping
from functools import cache, lru_cache

from ..schema import load
from .expressions import Undetermined, evaluate, parse_selector

RANK = {"optional": 0, "recommended": 1, "required": 2}


def rule(path: str):
    """Return the schema rule found at rules.<path>."""
    node = load().rules
    for part in path.split("."):
        node = node[part]
    return node


def level(requirement) -> str:
    """Return a requirement level written either "required" or {"level": "required", ...}."""
    return requirement if isinstance(requirement, str) else requirement["level"]


@cache
def rule_paths(group: str, marker: str = "selectors") -> tuple[str, ...]:
    """List the path of every rule under rules.<group>, a rule being a node that holds `marker`."""
    node = rule(group)
    if marker in node:
        return (group,)
    return tuple(path for key in node for path in rule_paths(f"{group}.{key}", marker))


def _applies(path: str, context: Mapping) -> bool | None:
    """Tell whether all selectors of a rule hold: True, False, or None when undetermined."""
    undetermined = False
    for selector in rule(path).selectors:
        try:
            if not evaluate(parse_selector(selector), context):
                return False
        except Undetermined:
            undetermined = True
    return None if undetermined else True


def _select(groups: tuple[str, ...], context: Mapping) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Split the rules of the given groups into those that apply and those left undetermined."""
    context = {"schema": load(), **context}
    applied, undetermined = [], []
    for group in groups:
        for path in rule_paths(group):
            verdict = _applies(path, context)
            if verdict is True:
                applied.append(path)
            elif verdict is None:
                undetermined.append(path)
    return tuple(applied), tuple(undetermined)


class _FrozenMap(tuple):
    """A mapping frozen into sorted (key, value) pairs, so that it can be hashed."""


class _FrozenScalar(tuple):
    """A scalar frozen with its type, so that True, 1 and 1.0 never share a cache entry."""


def _freeze(value):
    """Turn nested dicts and lists into hashable tuples (raises TypeError if a value cannot be hashed)."""
    if isinstance(value, Mapping):
        return _FrozenMap(sorted(((key, _freeze(item)) for key, item in value.items()), key=lambda pair: pair[0]))
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    hash(value)
    return _FrozenScalar((type(value), value))


def _thaw(value):
    """Undo _freeze."""
    if isinstance(value, _FrozenMap):
        return {key: _thaw(item) for key, item in value}
    if isinstance(value, _FrozenScalar):
        return value[1]
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


@lru_cache(maxsize=1024)
def _select_cached(groups: tuple[str, ...], frozen_context) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Cache the rule selection for each distinct file context."""
    return _select(groups, _thaw(frozen_context))


def applicable(groups: tuple[str, ...], context: Mapping) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return (applied, undetermined) rules of the given groups for a file context."""
    try:
        frozen = _freeze(context)
    except TypeError:
        return _select(groups, context)
    return _select_cached(groups, frozen)


def filename_rules(context: Mapping) -> tuple[str, ...]:
    """Return the rules.files.raw rules whose datatypes, suffixes and extensions cover the file."""
    return tuple(
        path for path in rule_paths("files.raw", marker="suffixes")
        if context.get("datatype") in rule(path).datatypes
        and context.get("suffix") in rule(path).suffixes
        and context.get("extension") in rule(path).extensions
    )


def single(paths: tuple[str, ...], kind: str, context: Mapping) -> str:
    """Return the only rule of a kind that applies to a file, or raise if there is none or several."""
    if not paths:
        raise ValueError(f"no {kind} rule applies to the file context {dict(context)}")
    if len(paths) > 1:
        raise NotImplementedError(f"several {kind} rules apply ({', '.join(paths)}); merging them is not supported")
    return paths[0]


@cache
def merged_fields(paths: tuple[str, ...]) -> dict[str, tuple[str, str]]:
    """Merge the fields of several rules into {field: (level, rule)}, keeping the strongest level."""
    merged = {}
    for path in paths:
        for field, requirement in rule(path).fields.items():
            strength = level(requirement)
            if field not in merged or RANK[strength] > RANK[merged[field][0]]:
                merged[field] = (strength, path)
    return merged
