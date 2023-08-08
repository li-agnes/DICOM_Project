# EDF to DICOM Converter

This script is designed to convert EDF (European Data Format) files, commonly used for storing physiological signals such as EEG (Electroencephalogram) data, into DICOM (Digital Imaging and Communications in Medicine) files. The script utilizes the pyedflib and pydicom libraries to perform the conversion and generate the necessary DICOM attributes.

The EDF to DICOM converter showcased in this script holds the potential to reshape neurophysiology practices by seamlessly translating data from the EDF format to the established DICOM standard. This conversion not only streamlines the integration of neurophysiological data into medical imaging and healthcare systems, enhancing clinical diagnosis and patient care, but also fosters collaborative research endeavors by enabling standardized data exchange across institutions.

## Requirements

Before using this script, ensure that you have the following Python libraries installed:

- **pyedflib**
- **pydicom**

You can install these libraries using the following commands:

`pip install pyedflib`
`pip install pydicom`

## Usage

To convert an EDF file to a DICOM file, follow these steps:

Save the script in a file (edf_to_dicom.py).
Open a terminal or command prompt.
Navigate to the directory containing the script and the EDF file.
Run the script with the EDF file as the argument:

`python edf_to_dicom.py input.edf`

Replace input.edf with the path to your EDF file. The script will generate a corresponding DICOM file with the same base name in the same directory.

## Script Functionality

The script performs the following tasks:

Opens the EDF file using pyedflib.EdfReader.
Creates a blank DICOM object and populates it with basic attributes.
Retrieves relevant information from the EDF header and sets DICOM metadata.
Creates DICOM datasets for each channel's waveform, functional groups, and annotations.
Sets various attributes related to EEG data.
Validates the DICOM dataset for conformity and integrity.
Generates a DICOM file and saves it with a '.dcm' extension.

## Additional Notes

The script generates DICOM files compatible with EEG data, but some attributes may need modification for other types of physiological data.
The script provides functions to read and validate the generated DICOM file.

## Disclaimer

This script is provided as a basic example and may require adjustments to match your specific use case or requirements. It's recommended to review and adapt the script as needed before using it for production purposes.