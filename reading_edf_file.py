import pyedflib
from pyedflib import highlevel
import numpy as np

#This file is for playing around with pyedflib and learning how to read/write EDF files

edf_file_path = "/Users/agnesli/Desktop/DICOM_Project/chb01_01.edf"
f = pyedflib.EdfReader(edf_file_path)
#edf_writer = pyedflib.EdfWriter(edf_file_path, 'a')


n = f.signals_in_file
print("Signals in file: ", n)

signal_labels = f.getSignalLabels()
print("Signal Labels: ", signal_labels)

sigbufs = np.zeros((n, f.getNSamples()[0]))
print("Signal Buffers: ", sigbufs) # Signal buffers represent a single channel


# Get the EDF file header
header = f.getHeader()

# Print the header
for key, value in header.items():
    print(f"{key}: {value}")

sampling_frequency = f.getSampleFrequency(0)
print(sampling_frequency)

#file = open(edf_file_path, "rb")
#print(file.read(44).decode('ascii'))

print(f"File Name: {edf_file_path}")
print(f"File Duration: {f.file_duration} seconds")
print(f"Number of Signals: {f.signals_in_file}")
print(f"Start Date: {f.getStartdatetime().strftime('%Y-%m-%d')}")
print(f"Start Time: {f.getStartdatetime().strftime('%H:%M:%S')}")

# Print information for each signal
for i in range(f.signals_in_file):
    print(f"\nSignal {i + 1}:")
    print(f"Signal Label: {f.getLabel(i)}")
    print(f"Signal Physical Dimension: {f.getPhysicalDimension(i)}")
    print(f"Signal Sample Frequency: {f.getSampleFrequency(i)} Hz")
    print(f"Signal Physical Range: {f.getPhysicalMinimum(i)} - {f.getPhysicalMaximum(i)} {f.getPhysicalDimension(i)}")
    print(f"Signal Digital Range: {f.getDigitalMinimum(i)} - {f.getDigitalMaximum(i)}")
    print(f"Signal Transducer Type: {f.getTransducer(i)}")
    print(f"Signal Prefiltering: {f.getPrefilter(i)}")
    print(f"Number of Samples: {f.getNSamples()[i]}")

# Close the EDF file
f.close()

#edf_writer.close()