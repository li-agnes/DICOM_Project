import pyedflib
import pydicom
from pydicom.dataset import Dataset
from pydicom.sequence import Sequence
from pydicom.dataset import FileDataset
from pyedflib import highlevel
from pydicom import uid


def convert_edf_to_dicom(edf_file_path, dicom_file_path):
    '''
    Converts an EDF file to DICOM format by adding basic attributes.

    Arguments:
        edf_file_path (str): Path to the EDF file.
        dicom_file_path (str): Path to save the output DICOM file.

    Returns:
        None
    '''
    # Open the EDF file
    edf_file = pyedflib.EdfReader(edf_file_path)

    # Create a blank DICOM object
    ds = Dataset()

    # Set the required DICOM metadata
    ds.PatientName = "John Doe"
    ds.PatientID = "123456"
    ds.StudyDescription = "EEG Study"
    ds.SeriesDescription = "EEG Series"
    ds.Modality = "OT"  # "OT" for Other Modality, since DICOM doesn't have modality for EEGs
    ds.Manufacturer = "Mobile App"
    ds.SoftwareVersions = "Your Software Version"

    # Set the EEG data as the pixel data
    ds.PixelData = edf_file.readSignal(0)

    # Add the EEG channel information
    channel_seq = Sequence()
    for i in range(edf_file.signals_in_file):
        channel_item = Dataset()
        channel_item.ChannelDescription = edf_file.getSignalLabels()[i]
        channel_seq.append(channel_item)

    # Create a Dataset object to hold the Per-Frame Functional Groups (multi-frame image or a dynamic series)
    per_frame_func_groups_ds = Dataset()
    per_frame_func_groups_ds.ChannelSequence = channel_seq

    # Create a Sequence to hold the Per-Frame Functional Groups Dataset
    shared_func_groups_seq = Sequence([per_frame_func_groups_ds])

    # Assign the Sequence to SharedFunctionalGroupsSequence
    ds.SharedFunctionalGroupsSequence = shared_func_groups_seq

    # Set the required attributes in the File Meta Information Header
    ds.file_meta = Dataset()
    ds.file_meta.MediaStorageSOPClassUID = uid.ExplicitVRLittleEndian
    ds.file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    ds.file_meta.TransferSyntaxUID = uid.ImplicitVRLittleEndian

    # Set the necessary attributes for saving
    ds.is_little_endian = True
    ds.is_implicit_VR = True

    # Save the DICOM object to a file
    ds.save_as(dicom_file_path)
    print("Conversion complete.")

    # Save the DICOM object to a file with 'DICM' prefix in the header
    ds.save_as(dicom_file_path, write_like_original=False)


def read_dicom_data(dicom_file_path):
    '''
    Prints parts of the metadata in the header to see if our new DICOM file works.

    Arguments:
        dicom_file_path (str): Path to the DICOM file.

    Returns:
        None
    '''
    # Read the DICOM file
    ds = pydicom.dcmread(dicom_file_path)

    # Access DICOM metadata
    print("Patient Name:", ds.PatientName)
    print("Patient ID:", ds.PatientID)
    print("Study Description:", ds.StudyDescription)
    print("Series Description:", ds.SeriesDescription)
    print("Modality:", ds.Modality)
    print("Manufacturer:", ds.Manufacturer)
    print("Software Versions:", ds.SoftwareVersions)

    # Commenting this part out because the EEG pixel data is not in human readable form
    '''
    # Access pixel data (EEG data)
    eeg_data = ds.PixelData
    print("EEG Data:", eeg_data)

    # Access EEG channel information
    channel_seq = ds.SharedFunctionalGroupsSequence[0].ChannelSequence
    for channel_item in channel_seq:
        print("Channel Description:", channel_item.ChannelDescription)
    '''

# Testing
edf_file_path = "/Users/agnesli/Desktop/DICOM_Project/chb01_01.edf"
dicom_file_path = "/Users/agnesli/Desktop/DICOM_Project/chb01_01.dcm"

convert_edf_to_dicom(edf_file_path, dicom_file_path)
read_dicom_data(dicom_file_path)
