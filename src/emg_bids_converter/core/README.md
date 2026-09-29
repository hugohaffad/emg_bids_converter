# emg_bids_converter.core

The BIDS schema and the checks built on it. The BIDS schema used is bundled with
[`bidsschematools`](https://github.com/bids-standard/bids-specification/tree/master/tools/schemacode).


## Modules

| Module | Role |
|---|---|
| `schema.py` | Loads the BIDS schema once (`load()`, cached). |
| `validation/fields.py` | Checks one value against its definition. |
| `validation/expressions.py` | Evaluates schema selectors against a file context. |
| `validation/rules.py` | Navigates `schema.rules` and selects the rules that apply to a file. |
| `validation/objects.py` | Checks a whole file (filename entities, TSV row, JSON metadata) against those rules. |


## Usage

A file is described by a context (datatype, suffix, extension, or path); the schema decides
which rules apply. Each check comes in two forms:

- `check_*` raises on the first error and ignores warnings. Models call it in `__post_init__`.
- `*_issues` returns every error and warning as `Issue` objects, e.g. for the GUI.

```python
from emg_bids_converter.core import check_metadata, metadata_issues

context = {"datatype": "emg", "suffix": "emg", "extension": ".bdf"}
sidecar = {
    "EMGPlacementScheme": "Other", "EMGReference": "REF", "SamplingFrequency": 2000.0,
    "PowerLineFrequency": 50, "RecordingType": "continuous", "SoftwareFilters": "n/a",
    "TaskName": "mvc",
}

metadata_issues(sidecar, context)  # errors, plus a warning per missing recommended field
check_metadata(sidecar, context)   # ValueError: EMGPlacementSchemeDescription is required
                                   # by rules.sidecars.emg.EMGPlacementSchemeDescription
```
The same pattern applies to `check_row` / `row_issues` (TSV rows) and
`check_entities` / `entities_issues` (filename entities).
