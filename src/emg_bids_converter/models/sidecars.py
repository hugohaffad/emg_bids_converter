from dataclasses import dataclass


@dataclass(frozen=True)
class Sidecar:
    """Class implementing the fields of the *_emg.json file"""

    # Specific EMG fields MUST be present (Required)
    EMGPlacementScheme: str
    EMGReference: str
    SamplingFrequency: float
    PowerLineFrequency: float | str
    RecordingType: str
    SoftwareFilters: dict[str, dict] | str
    TaskName: str

    # Specific EMG fields SHOULD be present (Recommended)
    EMGChannelCount: int | None = None
    HardwareFilters: dict[str, dict] | str | None = None
    RecordingDuration: float | None = None

    # Specific EMG fields MAY be present (Optional)
    ElectrodeMaterial: str | None = None
    ElectrodeType: str | None = None
    EMGGround: str | None = None
    EpochLength: float | None = None
    Gain: float | None = None
    InterelectrodeDistance: float | None = None
    Preamplification: float | None = None
    SkinPreparation: str | None = None
    SubjectArtefactDescription: str | None = None
    TriggerChannelCount: int | None = None
    EMGPlacementSchemeDescription: str | None = None

    # Hardware fields
    Manufacturer: str | None = None
    ManufacturersModelName: str | None = None
    SoftwareVersions: str | None = None
    DeviceSerialNumber: str | None = None
    ElectrodeManufacturer: str | None = None
    ElectrodeManufacturersModelName: str | None = None

    # Task Information fields
    TaskDescription: str | None = None
    Instructions: str | None = None

    # Institution Information fields
    InstitutionName: str | None = None
    InstitutionAddress: str | None = None
    InstitutionalDepartmentName: str | None = None
