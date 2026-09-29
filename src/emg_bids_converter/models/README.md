# emg_bids_converter.models

The data models of a BIDS dataset. A model is validated when it is built, so any instance that exists  can be written
as valid BIDS.


## Models

Modality-agnostic models live at the root; models specific to a modality live in its subpackage.

| Module | Class | BIDS object |
|---|---|---|
| `dataset_description.py` | `DatasetDescription` | `dataset_description.json` |
| `participants.py` | `Participant` | one row of `participants.tsv` |
| `emg/sidecars.py` | `Sidecar` | `*_emg.json` |
| `emg/channels.py` | `Channel` | one row of `*_channels.tsv` |
| `emg/electrodes.py` | `Electrode` | one row of `*_electrodes.tsv` |
| `emg/coordinate_systems.py` | `CoordinateSystem` | `*_coordsystem.json` |
| `emg/entities.py` | `Entities` | the entities of an EMG recording's filename (`sub-`, `task-`, …) |
| `emg/recording.py` | `Recording` | one recording: its signal and every object above that describes it |

## Example

An invalid value raises as soon as the model is built, with the field and the allowed values in the message.

```python
from emg_bids_converter.models.emg.channels import Channel

Channel(name__channels="1", type__channels="EMG", units="mV", group__emg="IN1")
Channel(name__channels="1", type__channels="emg", units="mV")
# ValueError: invalid type__channels='emg': 'emg' is not one of ['ACCEL', 'ADC', ...]
```

## Adding a modality

Create a subpackage (`models/eeg/`, …) with one class per BIDS object of that modality,  each passing its own file
context to `core`.