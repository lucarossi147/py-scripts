import numpy as np
import struct
import matplotlib.pyplot as plt
import os
import csv
from concurrent.futures import ThreadPoolExecutor
from scipy import signal
def open_dat(filename):
    f = open(filename, "rb")
    f_cont = f.read()
    f.close()
    raw = struct.unpack("d" * (len(f_cont) // 8), f_cont)
    return np.array(raw)

#filepath = "C:\\Users\\Luca Rossi\\Desktop\\buoni\\buoni buoni\\NK-2-1-SARSx10-2nd_006.dat"
#sr = 250e3
#dt = 1/sr
#l = len(raw)
#t = np.arange(0,l) * dt
#rng = 10e-9
#res = 2 * rng /65536

def detect_events(filepath):
    raw = open_dat(filename=filepath)
    
    m = np.mean(raw)
    s = np.std(raw)

    th = m-3*s
    min_samples = 3
    NO_EVENT = 0
    COUNTING = 1
    EVENT = 2
    status = NO_EVENT
    count = 0

    events = []
    begin_of_event = 0
    end_of_event = 0
    b = [1/3, 1/3, 1/3]
    a = 1
    smoothed = signal.filtfilt(b,a, raw)
    idx = 0
    print("analyzing")
    for blurred_i in smoothed:
        if status == NO_EVENT:
            if blurred_i < th:
                begin_of_event = idx
                count = 1
                status = COUNTING
        elif status == COUNTING:
            if blurred_i < th:
                count += 1
                if count >= min_samples:
                    status = EVENT
            else:
                status = NO_EVENT
        elif status == EVENT:
            if blurred_i < th:
                end_of_event = idx
            if blurred_i > m:
                events.append([begin_of_event, end_of_event])
                status = NO_EVENT
        idx += 1
    print("done")
    extracted_events=np.array([])
    corrected_events = []
    for event in events:
        start, end = event
        ev_range = (end-start) * 2
        start = start - ev_range if start - ev_range > 0 else 0
        end = end + ev_range if end + ev_range < len(raw) - 1 else len(raw) - 1
        corrected_events.append([start, end])
        extracted_events = np.concatenate((extracted_events, raw[start:end]), axis=None)

    results_folder = os.path.join("C:\\","Users", "Luca Rossi", "Desktop","extracted events")
    if not os.path.exists(results_folder):
        os.mkdir(results_folder)
    f_name = filepath.split(os.sep).pop().removesuffix(".dat") 
    folder_name = results_folder+os.sep+f_name
    # print(folder_name)
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    extracted_dat_name = f_name+".dat"
    dat_path = folder_name+os.sep+extracted_dat_name
    details_path = folder_name+os.sep+"details.csv"
    with open(dat_path, 'wb') as your_dat_file:  
        your_dat_file.write(struct.pack('d'*len(extracted_events), *extracted_events))
    with open(details_path, 'w') as f:
        # create the csv writer
        writer = csv.writer(f)
        # write a row to the csv file
        writer.writerow(["Original file",filepath])
        writer.writerow(["Event begin index","Event end index"])
        writer.writerows(corrected_events)

def detect_only_on_results():
    file_of_files_to_check = os.path.join("C:\\","Users", "Luca Rossi", "Desktop","results.txt")
    f = open(file_of_files_to_check, "r")
    files = [r.removesuffix("\n") for r in f if r.split(os.sep).pop().startswith("N")]
    f.close()
    return files    

def detect_from_all_files():
    file_of_files_to_check = os.path.join("C:\\","Users", "Luca Rossi", "Desktop","dataset_tirocinio")
    filenames = []
    for root, dirs, files in os.walk(path_to_dir):
        for filename in files:
            if filename.endswith(".dat") and not filename.endswith("MonitorFile.dat"):
                filenames.append(os.path.join(root, filename))

    return [r for r in filenames if r.split(os.sep).pop().startswith("N")]


files = detect_from_all_files()
# files = detect_only_on_results()

with ThreadPoolExecutor() as executor:
    executor.map(detect_events, files)