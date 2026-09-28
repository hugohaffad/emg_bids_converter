from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetDescription:
    """Class implementing the fields of the dataset_description.json file."""
    Name: str
    BIDSVersion: str
    HEDVersion: str | list[str] | None = None
    DatasetLinks: dict[str, str] | None = None
    DatasetType: str | None = None
    License: str | None = None
    Authors: list[str] | None = None
    Keywords: list[str] | None = None
    Acknowledgements: str | None = None
    HowToAcknowledge: str | None = None
    Funding: list[str] | None = None
    EthicsApprovals: list[str] | None = None
    ReferencesAndLinks: list[str] | None = None
    DatasetDOI: str | None = None
    SourceDatasets: list[dict] | None = None
    GeneratedBy: list[dict] | None = None
