"""Selector evaluation: schema expressions against a file context."""

import re
from collections.abc import Mapping
from functools import cache

from bidsschematools.expressions import Array, BinOp, Element, Function, Property, RightOp, parse


class Undetermined(Exception):
    """Raised when a selector needs information the context does not provide."""


def _type(value) -> str:
    """Name a value's type the way schema selectors do."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    return "array" if isinstance(value, list) else "object"


def _intersects(a, b):
    """Return the items shared by two lists, or False if there are none."""
    if not isinstance(a, list) or not isinstance(b, list):
        return False
    return [item for item in a if item in b] or False


def _match(value, pattern) -> bool:
    """Tell whether a string contains a match for a regular expression."""
    return isinstance(value, str) and re.search(pattern, value) is not None


_FUNCTIONS = {"intersects": _intersects, "match": _match, "type": _type}

_LITERALS = {"true": True, "false": False, "null": None}


@cache
def parse_selector(selector: str):
    """Parse a selector once into the syntax tree built by bidsschematools."""
    return parse(selector)


def evaluate(node, context: Mapping):
    """Evaluate a selector syntax tree against a file context."""
    if isinstance(node, (int, float)):
        return node
    if isinstance(node, str):
        if node[:1] in "\"'":
            return node[1:-1]
        if node in _LITERALS:
            return _LITERALS[node]
        return context.get(node)
    if isinstance(node, Array):
        return [evaluate(item, context) for item in node.elements]
    if isinstance(node, Property):
        parent = evaluate(node.name, context)
        return parent.get(node.field) if isinstance(parent, Mapping) else None
    if isinstance(node, Element):
        parent, index = evaluate(node.name, context), evaluate(node.index, context)
        return parent[index] if isinstance(parent, list) and isinstance(index, int) and index < len(parent) else None
    if isinstance(node, RightOp):
        if node.op != "!":
            raise Undetermined(f"operator {node.op!r} is not supported")
        return not evaluate(node.rh, context)
    if isinstance(node, BinOp):
        if node.op == "&&":
            return evaluate(node.lh, context) and evaluate(node.rh, context)
        if node.op == "||":
            return evaluate(node.lh, context) or evaluate(node.rh, context)
        left, right = evaluate(node.lh, context), evaluate(node.rh, context)
        if node.op == "==":
            return left == right
        if node.op == "!=":
            return left != right
        if node.op == "in":
            return isinstance(right, (list, Mapping, str)) and left in right
        raise Undetermined(f"operator {node.op!r} is not supported")
    if isinstance(node, Function) and node.name in _FUNCTIONS:
        return _FUNCTIONS[node.name](*(evaluate(arg, context) for arg in node.args))
    raise Undetermined(f"{node} cannot be evaluated here")
