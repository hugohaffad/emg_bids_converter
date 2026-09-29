import pytest

from emg_bids_converter.models.dataset_description import DatasetDescription


def test_dataset_description_valid():
    DatasetDescription(Name="my dataset", BIDSVersion="1.11.1")


def test_dataset_description_name_cannot_be_empty():
    with pytest.raises(ValueError, match="Name"):
        DatasetDescription(Name="", BIDSVersion="1.11.1")


def test_dataset_description_type_enum():
    DatasetDescription(Name="my dataset", BIDSVersion="1.11.1", DatasetType="raw")
    with pytest.raises(ValueError, match="DatasetType"):
        DatasetDescription(Name="my dataset", BIDSVersion="1.11.1", DatasetType="processed")


def test_dataset_description_authors_must_be_list_of_strings():
    DatasetDescription(Name="my dataset", BIDSVersion="1.11.1", Authors=["Hugo Haffad"])
    with pytest.raises(TypeError, match="Authors"):
        DatasetDescription(Name="my dataset", BIDSVersion="1.11.1", Authors="Hugo Haffad")


def test_dataset_description_derivative_requires_generated_by():
    with pytest.raises(ValueError, match="GeneratedBy"):
        DatasetDescription(Name="my dataset", BIDSVersion="1.11.1", DatasetType="derivative")


def test_dataset_description_generated_by_requires_name():
    DatasetDescription(Name="my dataset", BIDSVersion="1.11.1", GeneratedBy=[{"Name": "emg-bids-converter"}])
    with pytest.raises(ValueError, match="GeneratedBy"):
        DatasetDescription(Name="my dataset", BIDSVersion="1.11.1", GeneratedBy=[{"Version": "0.1.0"}])
