import numpy as np
import struct
import matplotlib.pyplot as plt
import os
import csv
from concurrent.futures import ThreadPoolExecutor
from scipy import signal
import time

def open_dat(filename):
    f = open(filename, "rb")
    f_cont = f.read()
    f.close()
    raw = struct.unpack("d" * (len(f_cont) // 8), f_cont)
    return np.array(raw)

def detect_events(filepath, file_number, results_folder):
    if file_number is not None:
        print("File number: " + str(file_number))
    if results_folder is not None:
        print("Results will be saved in "+ results_folder)
        if not os.path.exists(results_folder):
            print("Creating folder")
            os.mkdir(results_folder)

    raw = open_dat(filename=filepath)
    
    b = [1/5, 1/5, 1/5, 1/5, 1/5]
    a = 1
    smoothed = signal.filtfilt(b,a, raw)

    m = np.mean(smoothed)
    s = np.std(smoothed)

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
    if len(events) == 0:
        return
    for event in events:
        start, end = event
        ev_range = (end-start) * 2
        start = start - ev_range if start - ev_range > 0 else 0
        end = end + ev_range if end + ev_range < len(raw) - 1 else len(raw) - 1
        corrected_events.append([start, end])
        extracted_events = np.concatenate((extracted_events, raw[start:end]), axis=None)


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
    with open(details_path, 'w', newline="") as f:
        # create the csv writer
        writer = csv.writer(f)
        # write a row to the csv file
        writer.writerow(["Original file",filepath])
        writer.writerow(["Event begin index","Event end index"])
        writer.writerows(corrected_events)

def detect_only_on_results():
    path_of_files_to_check = os.path.join("C:\\","Users", "Luca Rossi", "Desktop","results.txt")
    f = open(path_of_files_to_check, "r")
    files = [r.removesuffix("\n") for r in f if r.split(os.sep).pop().startswith("N")]
    f.close()
    return files    

def get_dat_files(dir_path):
    filenames = []
    for root, dirs, files in os.walk(dir_path):
        for filename in files:
            if filename.endswith(".dat") and not filename.endswith("MonitorFile.dat"):
                filenames.append(os.path.join(root, filename))
    return filenames

start = time.time()
desktop_folder = os.path.join("C:\\","Users", "Luca Rossi", "Desktop")
folders_to_analyze = ["HCoV-229E", "MERS-CoV", "SARS-CoV", "SARS-CoV-2"]
results_folder_base = os.path.join(desktop_folder, "RESULTS")
if not os.path.exists(results_folder_base):
    os.mkdir(results_folder_base)
for fta in folders_to_analyze:
    results_folder = os.path.join(results_folder_base, fta)
    if not os.path.exists(results_folder):
        print("Creating resutls folder")
        os.mkdir(results_folder)
    else:
        print("Folder already exists")
    path_of_files_to_check = os.path.join(desktop_folder, "ml_data", "Cultured corona virus_I-t data", fta)
    # all folders containing relevant files to check
    all_folders_inside = os.listdir(path_of_files_to_check)
    all_number_folders = [os.path.join(path_of_files_to_check, f) for f in all_folders_inside]
    for number_folder in all_folders_inside:
        partial_result_folder = os.path.join(results_folder, number_folder)
        specific_number_folder_to_check = os.path.join(path_of_files_to_check, number_folder)
        if not os.path.exists(partial_result_folder):
            os.mkdir(partial_result_folder) 
        files = get_dat_files(specific_number_folder_to_check)
        # files = detect_only_on_results()
        print("Total number of files: " + str(len(files)))
        file_numbers = [n for n in range(len(files))]
        results_folder_list_to_pass = [partial_result_folder for n in range(len(files))]
        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.map(detect_events, files, file_numbers, results_folder_list_to_pass)
print(time.time()-start)