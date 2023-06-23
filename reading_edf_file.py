import pyedflib
from pyedflib import highlevel
import numpy as np

#This file is for playing around with pyedflib and learning how to read/write EDF files

edf_file_path = "/Users/agnesli/Desktop/DICOM Project/chb01_01.edf"
f = pyedflib.EdfReader(edf_file_path)
#edf_writer = pyedflib.EdfWriter(edf_file_path, 'a')


n = f.signals_in_file
print("Signals in file: ", n)

signal_labels = f.getSignalLabels()
print("Signal Labels: ", signal_labels)

sigbufs = np.zeros((n, f.getNSamples()[0]))
print("Signal Buffers: ", sigbufs) # Signal buffers represent a single channel


header = highlevel.make_header(technician="John Smith", equipment='Mobile App', patientname='Jane Doe', gender='Female', birthdate='01/02/2000')
print("Header: ", header)

#edf_writer.close()