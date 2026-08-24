class Metadata:
    """EMG-BIDS JSON sidecar fields"""
    def __init__(
            self,
            sampling_frequency,
            powerline_frequency,
            emg_placement_scheme,
            emg_reference,
            recording_type,
            software_filters,
            emg_placement_scheme_description,
            emg_channel_count = None,
            hardware_filters = None,
            task_name = None,
            task_description = None,
            manufacturer = None,
            emg_ground = None,
            interelectrode_distance = None,
            skin_preparation = None
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