"""Reader for OTB4 (.otb4) recording files."""

import re
import tarfile
import numpy as np
import xmltodict
from dataclasses import dataclass

from ..models.channels import Channel
from ..models.recording import Recording
from ..models.sidecars import Sidecar

_SENSOR_NAME_PATTERN = re.compile(r"^HD(\d+)MM\d+$")


@dataclass(frozen=True)
class Track:
    """Class implementing one track from an OTB4 file's Tracks_000.xml index."""
    title: str
    subtitle: str
    stream_path: str
    channels_in_block: int
    channel_offset: int
    n_channels: int
    adc_range: float
    adc_nbits: int
    gain: float
    unit: str
    unit_factor: float
    sensor: str
    ied: int
    sampling_frequency: float
    duration: float
    device: str
    mode: str
    low_pass_filter: str
    high_pass_filter: str

    @classmethod
    def from_xml(cls, node: dict) -> "Track":
        """Build a Track from one <TrackInfo> element"""
        description = node["Description"]
        strings = node["StringsDescriptions"]
        return cls(
            title=node["Title"],
            subtitle=node.get("SubTitle") or "",
            stream_path=node["SignalStreamPath"],
            channels_in_block=int(node["ChannelsInBlock"]),
            channel_offset=int(node["ChannelOffsetInSubPacket"]),
            n_channels=int(node["NumberOfChannels"]),
            adc_range=float(node["ADC_Range"]),
            adc_nbits=int(node["ADC_Nbits"]),
            gain=float(node["Gain"]),
            unit=node["UnitOfMeasurement"],
            unit_factor=float(node["UnitOfMeasurementFactor"]),
            sensor=strings["OriginalSensor"],
            ied=int(description["IED"]),
            sampling_frequency=float(node["SamplingFrequency"]),
            duration=float(node["TimeDuration"]),
            device=node["Device"],
            mode=strings["Mode"],
            low_pass_filter=strings["LowPassFilter"],
            high_pass_filter=strings["HighPassFilter"],
        )

    @property
    def is_emg(self) -> bool:
        return self.title.startswith("IN")

    @property
    def is_aux(self) -> bool:
        return self.subtitle.startswith("AUX")

    @property
    def interelectrode_distance(self) -> int:
        match = _SENSOR_NAME_PATTERN.match(self.sensor)
        if match is not None:
            return int(match.group(1))
        return self.ied

    def decode(self, raw_i32: np.ndarray) -> np.ndarray:
        """Convert this track's raw int32 buffer to physical units (self.unit)."""
        m = raw_i32.reshape((self.channels_in_block, -1), order="F")
        block = m[self.channel_offset:self.channel_offset + self.n_channels, :].astype(np.float32)
        scale = self.adc_range / (2 ** self.adc_nbits) * self.unit_factor / self.gain
        block *= scale
        return block


def read(path, task_name: str, emg_reference: str, powerline_frequency: float = 50) -> Recording:
    """Read an OTB4 file into a Recording."""
    if not emg_reference or not emg_reference.strip():
        raise ValueError("emg_reference is required")

    with tarfile.open(path, "r") as tar:
        index = xmltodict.parse(tar.extractfile("Tracks_000.xml"), force_list=("TrackInfo",))
        tracks = [Track.from_xml(node) for node in index["ArrayOfTrackInfo"]["TrackInfo"]]

        emg_tracks = sorted(
            (track for track in tracks if track.is_emg),
            key=lambda t: int("".join(c for c in t.title if c.isdigit())),
        )

        aux_tracks = sorted(
            (track for track in tracks if track.is_aux),
            key=lambda t: int("".join(c for c in t.subtitle if c.isdigit())),
        )

        blocks, channels = [], []
        first = emg_tracks[0]
        high_cutoff = round(float(first.low_pass_filter.split()[0]), 1)
        low_cutoff = round(first.sampling_frequency / 190, 1)

        for track in emg_tracks:
            raw_data = np.frombuffer(tar.extractfile(track.stream_path).read(), dtype=np.int32)
            block = track.decode(raw_data)
            blocks.append(block)

            for _ in range(block.shape[0]):
                channels.append(
                    Channel(
                        name__channels=str(len(channels) + 1),
                        type__channels="EMG",
                        units=track.unit,
                        group__emg=track.title,
                        interelectrode_distance=track.interelectrode_distance,
                        low_cutoff=low_cutoff,
                        high_cutoff=high_cutoff,
                    )
                )

        signal = np.vstack(blocks)

        sensors = sorted({track.sensor for track in emg_tracks if track.sensor})
        hardware_filters = {
            "LowPassFilter": {"Description": first.low_pass_filter},
            "HighPassFilter": {"Description": first.high_pass_filter},
        }

        metadata = Sidecar(
            EMGPlacementScheme="Other",
            EMGPlacementSchemeDescription="HDsEMG grid electrodes; exact positions not yet digitized",
            EMGReference=emg_reference,
            SamplingFrequency=first.sampling_frequency,
            PowerLineFrequency=powerline_frequency,
            RecordingType="continuous",
            SoftwareFilters="n/a",
            TaskName=task_name,
            EMGChannelCount=sum(t.n_channels for t in emg_tracks),
            HardwareFilters=hardware_filters,
            RecordingDuration=first.duration,
            Manufacturer="OT Bioelettronica",
            ManufacturersModelName=first.device,
            ElectrodeManufacturer="OT Bioelettronica",
            ElectrodeManufacturersModelName=", ".join(sensors) if sensors else None,
        )

    return Recording(
        signal=signal, channels=channels, electrodes=[], coordinate_systems={}, metadata=metadata
    )
