import pyedflib
import pydicom
from pydicom.dataset import Dataset
from pydicom.sequence import Sequence
from pydicom.dataset import FileDataset
from pyedflib import highlevel
from pydicom import uid
from pydicom.errors import InvalidDicomError
import numpy as np
import sys


### converting EDF info into DICOM format


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

    # Pull from EDF Header and set the DICOM metadata
    header = edf_file.getHeader()


    ds.PatientName = header['patientname']
    ds.StudyDate = edf_file.getStartdatetime().strftime("%Y%m%d")
    ds.StudyTime = edf_file.getStartdatetime().strftime("%H%M%S")
    ds.PatientBirthDate = header['birthdate']
    ds.PatientSex = header['gender']
    ds.PatientID = header['patientcode']
    ds.ManufacturerModelName = header['equipment']

    '''
    # Some more stuff found in the EDF header, need to find the corresponding DICOM element
    ds.technician = header['technician']
    ds.recording_additional = header['recording_additional']
    ds.patient_additional = header['patient_additional']
    ds.admin_code = header['admincode']
    '''

    ds.StudyDescription = "EEG Study"
    ds.SeriesDescription = "EEG Series"
    ds.Manufacturer = "Mobile App"
    ds.SoftwareVersions = "Your Software Version"

    # Create a Sequence to hold the Waveform Sequence
    waveform_sequence = Sequence()

    # Create a Sequence to hold the Per-Frame Functional Groups Dataset
    shared_func_groups_seq = Sequence()

    # Create a Sequence to hold the Waveform Annotation Sequence (0040,B020)
    waveform_annotation_sequence = Sequence()

    # Iterate over each channel in the EDF file
    for channel_idx in range(edf_file.signals_in_file):
        ## Create a Dataset for each channel's waveform
        waveform_ds = Dataset()

        # Set the waveform-specific attributes
        waveform_ds.SamplingFrequency = edf_file.getSampleFrequency(channel_idx)
        waveform_ds.WaveformBitsAllocated = 16
        waveform_ds.WaveformSampleInterpretation = "SS"

        # Set the EEG data as the waveform data
        waveform_ds.WaveformData = edf_file.readSignal(channel_idx)

        # Append the waveform Dataset to the Sequence
        waveform_sequence.append(waveform_ds)

        ## Create a Dataset to hold the Per-Frame Functional Groups (multi-frame image or a dynamic series) for this channel
        per_frame_func_groups_ds = Dataset()

        # Set the waveform Sequence to the Per-Frame Functional Groups Dataset for this channel
        per_frame_func_groups_ds.WaveformSequence = Sequence([waveform_ds])

        # Set the channel label for this channel's Per-Frame Functional Groups Dataset
        per_frame_func_groups_ds.ChannelLabel = edf_file.getLabel(channel_idx)

        # Append the Per-Frame Functional Groups Dataset to the Sequence
        shared_func_groups_seq.append(per_frame_func_groups_ds)

        ## Create a Dataset for each channel's Waveform Annotation
        waveform_annotation_ds = Dataset()

        # Set the channel label for this channel's Waveform Annotation Dataset
        waveform_annotation_ds.ChannelLabel = edf_file.getLabel(channel_idx)

        # Add the Concept Code Sequence (0040,A043) to the Waveform Annotation Dataset
        concept_code_sequence = Sequence()
        for cid in [3035, 3038, 3039, 3040]:
            item = Dataset()
            item.CodeValue = str(cid)
            item.CodingSchemeDesignator = "CID"
            item.CodeMeaning = "Concept Name"  # Replace with the appropriate name for each CID
            concept_code_sequence.append(item)

        waveform_annotation_ds.ConceptCodeSequence = concept_code_sequence

        # Append the Waveform Annotation Dataset to the Waveform Annotation Sequence
        waveform_annotation_sequence.append(waveform_annotation_ds)


    # Set the Sequence of Per-Frame Functional Groups to the DICOM object
    ds.SharedFunctionalGroupsSequence = shared_func_groups_seq


    # Routine Scalp EEG specific attributes
    ds.Modality = "EEG"
    ds.WaveformBitsAllocated = 16
    ds.WaveformSampleInterpretation = "SS"
    ds.NumberOfWaveformChannels = len(edf_file.getSignalLabels())

    # Set the required attributes in the File Meta Information Header
    ds.file_meta = Dataset()
    ds.file_meta.MediaStorageSOPClassUID = uid.ExplicitVRLittleEndian
    ds.file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    ds.file_meta.TransferSyntaxUID = uid.ImplicitVRLittleEndian


    # Set the necessary attributes for saving
    ds.is_little_endian = True
    ds.is_implicit_VR = True

    # Save the DICOM object to a file with 'DICM' prefix in the header
    ds.save_as(dicom_file_path, write_like_original=False)
    print("Conversion complete.")



def read_dicom_data(dicom_file_path):
    '''
    Prints parts of the new DICOM file.

    Arguments:
        dicom_file_path (str): Path to the DICOM file.

    Returns:
        None
    '''
    # Read the DICOM file
    ds = pydicom.dcmread(dicom_file_path)

    # Access DICOM metadata
    print(ds)


def validate_dicom_file(dicom_file_path):
    '''
    Checks if the DICOM dataset conforms to the DICOM standard and verifies the 
    integrity of the dataset structure

    Arguments:
        dicom_file_path (str): Path to the DICOM file.
    '''

    try:
        pydicom.dcmread(dicom_file_path)
        print("DICOM file is valid.")
    except InvalidDicomError:
        print("DICOM file is invalid.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py input.edf")
        sys.exit(1)

    edf_file_path = sys.argv[1]
    dicom_file_path = edf_file_path.replace(".edf", ".dcm")

    convert_edf_to_dicom(edf_file_path, dicom_file_path)
    read_dicom_data(dicom_file_path)
    validate_dicom_file(dicom_file_path)