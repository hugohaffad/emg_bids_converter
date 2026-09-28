import pytest

from emg_bids_converter.models.channels import Channel


def test_channel_valid():
    Channel(name__channels="ch1", type__channels="EMG", units="mV")


def test_channel_name_cannot_be_empty():
    with pytest.raises(ValueError, match="name"):
        Channel(name__channels="  ", type__channels="EMG", units="mV")


def test_channel_units_cannot_be_empty():
    with pytest.raises(ValueError, match="units"):
        Channel(name__channels="ch1", type__channels="EMG", units=" ")


def test_channel_type_must_be_uppercase():
    with pytest.raises(ValueError, match="type__channels"):
        Channel(name__channels="ch1", type__channels="emg", units="mV")


def test_channel_status_enum():
    with pytest.raises(ValueError, match="status"):
        Channel(name__channels="ch1", type__channels="EMG", units="mV", status="ok")


def test_channel_accepts_valid_status():
    Channel(name__channels="ch1", type__channels="EMG", units="mV", status="good")


def test_channel_group_accepts_string_or_number():
    Channel(name__channels="ch1", type__channels="EMG", units="mV", group__emg="grid1")
    Channel(name__channels="ch1", type__channels="EMG", units="mV", group__emg=1)


def test_channel_sampling_frequency_must_be_number():
    with pytest.raises(TypeError, match="sampling_frequency"):
        Channel(name__channels="ch1", type__channels="EMG", units="mV", sampling_frequency="fast")


def test_channel_notch_must_be_string():
    with pytest.raises(TypeError, match="notch"):
        Channel(name__channels="ch1", type__channels="EMG", units="mV", notch=60)
