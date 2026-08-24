class Metadata:
    """EMG-BIDS JSON sidecar fields"""
    def __init__(
            self,
            sampling_frequency,                         # REQUIRED – Sampling rate in Hz
            powerline_frequency,                        # REQUIRED – Power line frequency (50 or 60 Hz)
            emg_placement_scheme,                       # REQUIRED – How electrode locations were determined: "Measured", "ChannelSpecific", or "Other"
            emg_reference,                              # REQUIRED – Reference electrode specification or "Bipolar" for paired sensors
            recording_type,                             # REQUIRED – Data continuity: "continuous", "epoched",  or "discontinuous"
            software_filters,                           # REQUIRED – Digital filters applied, or "n/a"
            emg_placement_scheme_description = None,    # REQUIRED only if EMGPlacementScheme is marked as “Other”
            emg_channel_count = None,                   # RECOMMENDED – Number of EMG channels
            hardware_filters = None,                    # RECOMMENDED – Analog filter specifications
            task_name = None,                           # RECOMMENDED – Short task identifier
            task_description = None,                    # RECOMMENDED – Detailed task description
            manufacturer = None,                        # RECOMMENDED – Recording system manufacturer
            emg_ground = None,                          # OPTIONAL – Ground electrode location
            interelectrode_distance = None,             # OPTIONAL – Distance between electrode pairs (mm)
            skin_preparation = None                     # OPTIONAL – Skin preparation procedure
    ):
        self.sampling_frequency = sampling_frequency
        self.powerline_frequency = powerline_frequency
        self.emg_placement_scheme = emg_placement_scheme
        self.emg_reference = emg_reference
        self.recording_type = recording_type
        self.software_filters = software_filters
        self.emg_placement_scheme_description = emg_placement_scheme_description
        self.emg_channel_count = emg_channel_count
        self.hardware_filters = hardware_filters
        self.task_name = task_name
        self.task_description = task_description
        self.manufacturer = manufacturer
        self.emg_ground = emg_ground
        self.interelectrode_distance = interelectrode_distance
        self.skin_preparation = skin_preparation

class Channel:
    """Channel: a single analog-to-digital converter in the recording system that regularly samples the value of a
    transducer, which results in the signal being represented as a time series in the digitized data"""
    def __init__(
            self,
            name,                       # REQUIRED – Channel identifier matching data file
            type,                       # REQUIRED – Channel type (EMG, ECG, REF, etc.)
            units,                      # REQUIRED – Physical units (e.g., uV, mV)
            signal_electrode = None,    # RECOMMENDED – Name of signal electrode in * electrodes.tsv
            reference = None,           # RECOMMENDED – Reference electrode name
            target_muscle = None,       # RECOMMENDED – Anatomical muscle name
            group = None,               # RECOMMENDED – Device or array identifier
            sampling_frequency = None   # OPTIONAL – If different from rate specified in sidecar file
    ):
        self.name = name
        self.type = type
        self.units = units
        self.signal_electrode = signal_electrode
        self.reference = reference
        self.target_muscle = target_muscle
        self.group = group
        self.sampling_frequency = sampling_frequency

class Electrode:
    """Electrode: a single point of contact between the acquisition system and the recording site"""
    def __init__(
            self,
            name,                       # REQUIRED – Electrode identifier
            x,                          # REQUIRED – X coordinate
            y,                          # REQUIRED – Y coordinate
            z = None,                   # OPTIONAL – Z coordinate
            coordinate_system = None,   # RECOMMENDED – Reference to space-<label> coordsystem.json
            group = None                # RECOMMENDED – Array or device identifier
    ):
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.coordinate_system = coordinate_system
        self.group = group

class CoordinateSystem:
    def __init__(
            self,
            parent_coordinate_system,
            anchor_electrode,
            anchor_coordinates
    ):
        self.parent_coordinate_system = parent_coordinate_system
        self.anchor_electrode = anchor_electrode
        self.anchor_coordinates = anchor_coordinates