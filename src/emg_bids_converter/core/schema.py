"""Load the BIDS schema once, then reuse it."""

from functools import cache

from bidsschematools import schema as bst
from bidsschematools.types import Namespace


@cache
def load() -> Namespace:
    return bst.load_schema()
