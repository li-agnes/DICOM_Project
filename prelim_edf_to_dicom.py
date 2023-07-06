import pyedflib
import pydicom
from pydicom.dataset import Dataset
from pydicom.sequence import Sequence
from pydicom.dataset import FileDataset
from pyedflib import highlevel
from pydicom import uid
from pydicom.errors import InvalidDicomError
import numpy as np



### code from read_edfD.py that prints parts of the EDF


#-----------------------------------------
# Add seconds to date/time
#-----------------------------------------
def add_seconds(date, time, secs):
    # Convert the strings to a datetime object
    a = range(3)
    ymd = date.split('.')
    y,m,d = [int(ymd[i]) for i in a]
    hms = time.split('.')
    h,min,s = [int(hms[i]) for i in a]
    dt = datetime.datetime(y,m,d,h,min,s)
    
    print("old date, time = ", date, time,"; dt = ", secs)


    # Add the given number of seconds
    new_dt = dt + datetime.timedelta(seconds=secs)
    
    # Convert the datetime object back to strings
    new_date = new_dt.date().strftime("%2Y.%m.%d")
    new_time = new_dt.time().strftime("%H.%M.%S")
    
    return new_date, new_time

#-----------------------------------------
# Read the edf file and print some information
#-----------------------------------------
def read_edfD(edf_file_path):
    
    print("reading data from ", edf_file_path)
    
    # Create a record to hold the size of the header and data 
    # records and location of continuous segments
    record = {}
    record["nhead"] = 0 
    record["nrecords"] = []
    record["nr"] = 0
    record["ns"] = 0
    record["start"] = [] 
    record["nheadbytes"] = 0

    # Read the file and print the text field
    file = open(edf_file_path, "rb")
    
    # Get header information
    version = file.read(8).decode('ascii')
    patient = file.read(80).decode('ascii')
    localrecID = file.read(80).decode('ascii')
    startdate = file.read(8).decode('ascii')
    starttime = file.read(8).decode('ascii')
    record["start"].append([startdate, starttime])
    print("Patient field: ", patient)
    print("startdate: ", startdate)
    print("starttime: ", starttime)

    nheadbytes = file.read(8).decode('ascii')
    reserved1 = file.read(44).decode('ascii')
    print("reserved1 = ", reserved1)
    nr = int(file.read(8).decode('ascii'))  # number of records
    rec_in_secs = float(file.read(8).decode('ascii'))
    ns = int(file.read(4).decode('ascii'))  # number of signals
    nhead = int(nheadbytes)
    record["nhead"] = nhead
    record["nr"] = nr
    record["ns"] = ns
    
    edf_type = reserved1
    print("EDF+ type: ", edf_type)
    print("version: ", version)
    print("nr, ns, rec_in_secs: ", nr, ns, rec_in_secs)

    #print("Step 1, position = ", file.tell())
   
    # Read header data for each signal
    new_ch_names = []
    transducer = []
    physical_dim = []
    physical_min = []
    physical_max = []
    digital_min = []
    digital_max = []
    prefiltering = []
    nsr = []
    reserved2 = []
    for i in range(ns): new_ch_names.append(file.read(16).decode('ascii').strip())
    for i in range(ns): transducer.append(file.read(80).decode('ascii'))
    for i in range(ns): physical_dim.append(file.read(8).decode('ascii'))
    for i in range(ns): physical_min.append(file.read(8).decode('ascii'))
    for i in range(ns): physical_max.append(file.read(8).decode('ascii')) 
    for i in range(ns): digital_min.append((file.read(8).decode('ascii')))
    for i in range(ns): digital_max.append((file.read(8).decode('ascii')))
    for i in range(ns): prefiltering.append(file.read(80).decode('ascii'))
    for i in range(ns): nsr.append(int(file.read(8).decode('ascii')))
    for i in range(ns): reserved2.append(file.read(32).decode('ascii'))   
    record["nsr"] = nsr
    
    srate = nsr[0]/rec_in_secs
    print("srate = ", srate)
    print("Channel names: ", new_ch_names)
    print("Number of channels = ", len(new_ch_names))
    print("End of header, position = ", file.tell())
   
    # Data streams
    nsr_last = nsr[ns-1] # number of annotation entries in each record
    data = []
    edf_annotation = []
    for s in range(ns):
        data.append([])
    print("n records = ", nr)
    m = sum(nsr[0:ns-1])  # add up the number of seconds per record (nsr) for each signal
    btyes_per_record = m*2  # 2 bytes per data entry; m is the number of bytes per record
    print("Reading info for %d records ... " %(nr))
    for r in range(nr):  # Loop over records
        file.seek(btyes_per_record, 1)
        if r%1000 == 0: print("... record ", r)
        #for s in range(ns-1):
        #    data[s].extend(np.fromfile(file, dtype=np.int16,sep="", count=nsr[s]))
        
        edf_annotation.append(np.fromfile(file, dtype=np.byte,sep="", count=2*nsr_last))
       
    # Let's scale the data
    scale = 1.0
    
    physical_min = np.asarray(physical_min, dtype=float)
    physical_max = np.asarray(physical_max, dtype=float)
    digital_min = np.asarray(digital_min, dtype=float)
    digital_max = np.asarray(digital_max, dtype=float)
    print("phys min/max = ", physical_min[0], physical_max[0])
    print("digi min/max = ", digital_min[0], digital_max[0])
    m = np.zeros(ns-1)
    for s in range(ns-1):
        if   'mV' in physical_dim[0]: scale = 1.0e-3
        elif 'uV' in physical_dim[0]: scale = 1.0e-6
        elif 'nV' in physical_dim[0]: scale = 1.0e-9
        m[s] = (physical_max[s]-physical_min[s])/(digital_max[s]-digital_min[s])
        b = 0.0 #physical_min[s]
        data[s] = scale*(m[s]*np.asarray(data[s], dtype=float) + b)
    print("data:     ", data[2][0:5])
    
    # Search for discontinuities
    startdate0, starttime0 = startdate, starttime
    r0 = 0
    rn = nr-1    
    if "EDF+D" in edf_type:
        a = edf_annotation    
        rec_start = []
        for i in range(nr):
            c = a[i].tobytes().decode('ascii').split('+')
            a1 = c[1].replace("\x14", "")
            a2 = a1.replace("\x00", "")
            a3 = round(float(a2),3)
            rec_start.append(a3)
            
        t0 = rec_start[r0]
        tn = rec_start[rn]
        segments = [[t0,tn]]
        isegments = [[r0,rn]]

        s = 0
        for r in range(1,nr):
            t1 = rec_start[r]
            r1 = r
            
            dt = round(t1-t0,3)
            if dt > rec_in_secs:
                print("Gap in records %d to %d of %8.3f " % (r0, r1, t1-t0))
                segments[s][1] = t0
                isegments[s][1] = r0
                segments.append([t1,tn])
                isegments.append([r1,rn])
                
                startdate, starttime = add_seconds(startdate0, starttime0, t1)
                record["start"].append([startdate, starttime])
                s += 1
            
            t0 = t1
            r0 = r1
    else:
        t0 = 0.0
        t1 = nr*nsr[0]/srate
        segments = [[t0,t1]]
        isegments = [[r0,rn]]
                        
    nsegs = len(segments)
    record["nsegments"] = nsegs
    print("Total number of segments = ", len(segments))
    for s in range(len(segments)):
        r0 = isegments[s][0]
        rn = isegments[s][1]
        record["nrecords"].append(rn-r0+1)
        print("segment ", s+1, ": ", segments[s], "; records: ", isegments[s]," (hours: ",segments[s][1]/3600.0,")")
        print("   nrecords = ", record["nrecords"][s])
    file.close() 
           
    return record


#-----------------------------------------
# Change startdate, starttime, nr in EDF header
#-----------------------------------------
def set_header(header, record):
    # startdate: 8 bytes, starting at byte 168
    # starttime: 8 bytes, starting at byte 176
    # edf_type:  44 bytes starting at byte 192
    # nr:        8 bytes, starting at byte 236
    
    # Get the needed information
    startdate = record["start"][i][0]
    starttime = record["start"][i][1]
    nr = record["nrecords"][i]
    
    # We're writing a continuous file
    edf_type = "EDF+C"
    
    # convert the integer nr to an 8-byte string
    nr8 = str("%-8d" %(nr))  
    
    # Convert the header to a character list (strings are immutable)
    header_list = list(header.decode('ascii'))  
    
    # Replace precise characters (byte locations) in the character list
    header_list[168:176] = startdate
    header_list[176:184] = starttime
    header_list[192:197] = edf_type
    header_list[236:244] = nr8
    
    # Convert back to bytes
    bheader = bytes("".join(header_list), 'utf-8')
    
    return bheader



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

    # Set the EEG data as the pixel data
    ds.pixel_data = edf_file.readSignal(0)

    # Create a Sequence to hold the Per-Frame Functional Groups Dataset
    shared_func_groups_seq = Sequence()

    # Iterate over each channel in the EDF file
    for channel_idx in range(edf_file.signals_in_file):
        # Create a Dataset for each channel
        channel_ds = Dataset()

        # Set the channel-specific attributes
        channel_ds.ChannelLabel = edf_file.getLabel(channel_idx)

        # Create a Dataset to hold the Per-Frame Functional Groups (multi-frame image or a dynamic series)
        per_frame_func_groups_ds = Dataset()
        per_frame_func_groups_ds.ChannelSourceSequence = Sequence([channel_ds])

        # Append the Per-Frame Functional Groups Dataset to the Sequence
        shared_func_groups_seq.append(per_frame_func_groups_ds)

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


    channel_source_seq = Sequence()
    for i in range(edf_file.signals_in_file):
        channel_source_item = Dataset()
        # code sequence for the channel source
        channel_source_item.channel_source_code_sequence = Sequence([
            Dataset(
                CodeValue="EEG Leads",
                CodingSchemeDesignator="CID 3030",
                CodingSchemeVersion="",
                CodeMeaning="EEG Leads"
            )
        ])
        # modifiers, which are additional specifications related to the channel source
        channel_source_item.ChannelSourceModifiersSequence = Sequence([
            Dataset(
                CodeValue="Differential signal",
                CodingSchemeDesignator="CID 3240",
                CodingSchemeVersion="",
                CodeMeaning="Differential signal"
            ),
            Dataset(
                CodeValue="EEG Leads",
                CodingSchemeDesignator="CID 3030",
                CodingSchemeVersion="",
                CodeMeaning="EEG Leads"
            )
        ])

    # Add the Channel Source and Channel Source Modifiers to the Sequence
    channel_source_seq.append(channel_source_item)

    # Set the Channel Source and Channel Source Modifiers
    per_frame_func_groups_ds.ChannelSourceSequence = channel_source_seq

    # Set the necessary attributes for saving
    ds.is_little_endian = True
    ds.is_implicit_VR = True

    # Save the DICOM object to a file with 'DICM' prefix in the header
    ds.save_as(dicom_file_path, write_like_original=False)
    print("Conversion complete.")



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


# Testing
edf_file_path = "/Users/agnesli/Desktop/DICOM_Project/chb01_01.edf"
dicom_file_path = "/Users/agnesli/Desktop/DICOM_Project/chb01_01.dcm"

#read_edfD(edf_file_path)

convert_edf_to_dicom(edf_file_path, dicom_file_path)
read_dicom_data(dicom_file_path)
validate_dicom_file(dicom_file_path)
