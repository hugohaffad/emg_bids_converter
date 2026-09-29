from functools import cache
from bidsschematools import schema as bst
from bidsschematools.types import Namespace


@cache
def load() -> Namespace:
    """Load the BIDS schema, then add it to the cache."""
    return bst.load_schema()
