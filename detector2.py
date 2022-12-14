import numpy as np
import struct
import os
import csv
from concurrent.futures import ThreadPoolExecutor
from scipy import signal
import time


def open_dat(filename):
    file = open(filename, "rb")
    f_cont = file.read()
    file.close()
    raw = struct.unpack("d" * (len(f_cont) // 8), f_cont)
    return np.array(raw)


def detect_events(filepath, file_number, res_folder):
    if file_number is not None:
        print("File number: " + str(file_number))
    if res_folder is not None:
        # print("Results will be saved in " + res_folder)
        if not os.path.exists(res_folder):
            # print("Creating folder")
            os.mkdir(res_folder)

    raw = open_dat(filename=filepath)

    mov_avg_length_mono = 5000
    mov_avg_length = mov_avg_length_mono * 2 + 1
    min_event_l = 10
    max_event_length_mono = 250
    max_event_length = max_event_length_mono * 2 + 1
    max_std = 0.2e-9
    mov_avg_den = mov_avg_length - max_event_length
    min_noise_ratio = 2
    b = [1 / 3, 1 / 3, 1 / 3]
    a = 1
    sr = 250000
    blf, alf = signal.butter(4, 1000 / (sr / 2), 'low')
    smoothed = signal.filtfilt(b, a, raw)
    smoothed = smoothed[mov_avg_length_mono + 1:len(smoothed) - mov_avg_length_mono]
    low_freqs_data = signal.filtfilt(blf, alf, raw)
    cs = np.cumsum(raw)
    cs2 = np.cumsum(np.power(raw, 2))
    # cumsum low freqs
    cslf = np.cumsum(low_freqs_data)
    cs2lf = np.cumsum(np.power(low_freqs_data, 2))
    center = np.array(range(mov_avg_length_mono + 1, len(raw) - mov_avg_length_mono))
    m = (cs[center + mov_avg_length_mono] - cs[center + max_event_length_mono] + cs[
        center - 1 - max_event_length_mono] - cs[center - 1 - mov_avg_length_mono]) / mov_avg_den
    s = np.sqrt((cs2[center + mov_avg_length_mono] - cs2[center + max_event_length_mono] + cs2[
        center - 1 - max_event_length_mono] - cs2[center - 1 - mov_avg_length_mono]) / mov_avg_den - np.power(m, 2))

    mlf = (cslf[center + mov_avg_length_mono] - cslf[center + max_event_length_mono] + cslf[
        center - 1 - max_event_length_mono] - cslf[center - 1 - mov_avg_length_mono]) / mov_avg_den
    slf = np.sqrt((cs2lf[center + mov_avg_length_mono] - cs2lf[center + max_event_length_mono] + cs2lf[
        center - 1 - max_event_length_mono] - cs2lf[center - 1 - mov_avg_length_mono]) / mov_avg_den - np.power(mlf, 2))
    noise_ratio = s / slf
    th = m + 3 * s
    NO_EVENT = 0
    COUNTING = 1
    EVENT = 2
    NOISE = 3
    status = NO_EVENT
    count = 0
    noise_count = 0
    events = []
    begin_of_event = 0
    end_of_event = 0
    poop_fuck = 0
    print("analyzing")
    for i in range(len(center)):
        if status == NO_EVENT:
            if noise_ratio[i] < min_noise_ratio:
                noise_count += 1
            else:
                noise_count = 0
            if noise_count > mov_avg_length_mono:
                status = NOISE
                continue
            if s[i] > max_std:
                continue
            if smoothed[i] > th[i]:
                begin_of_event = i
                count = 1
                status = COUNTING
        elif status == COUNTING:
            if smoothed[i] > th[i]:
                count += 1
                end_of_event = i
                if count >= min_event_l:
                    status = EVENT
            else:
                status = NO_EVENT
        elif status == EVENT:
            if count > max_event_length:
                status = NO_EVENT
                continue
            count += 1
            if smoothed[i] > th[i]:
                end_of_event = i
            if smoothed[i] < m[i] and end_of_event > begin_of_event and count > min_event_l:
                if poop_fuck < end_of_event - begin_of_event:
                    poop_fuck = end_of_event - begin_of_event
                events.append([begin_of_event, end_of_event])
                status = NO_EVENT
        elif status == NOISE:
            if noise_ratio[i] > min_noise_ratio:
                status = NO_EVENT
                noise_count = 0
    print("done, found events are: ", len(events))
    extracted_events = np.array([])
    corrected_events = []
    if len(events) == 0:
        return
    for event in events:
        start, end = event
        start += mov_avg_length_mono
        end += mov_avg_length_mono
        ev_range = (end - start) * 2
        start = start - ev_range if start - ev_range > 0 else 0
        end = end + ev_range if end + ev_range < len(raw) - 1 else len(raw) - 1
        corrected_events.append([start, end])
        extracted_events = np.concatenate((extracted_events, raw[start:end]), axis=None)

    f_name = filepath.split(os.sep).pop()
    dat_path = os.path.join(res_folder, f_name)
    details_path = os.path.join(res_folder, "details.csv")
    with open(dat_path, 'wb') as your_dat_file:
        your_dat_file.write(struct.pack('d' * len(extracted_events), *extracted_events))
    with open(details_path, 'w', newline="") as f:
        # create the csv writer
        writer = csv.writer(f)
        # write a row to the csv file
        writer.writerow(["Original file", filepath])
        writer.writerow(["Event begin index", "Event end index"])
        writer.writerows(corrected_events)


def get_dat_files(dir_path):
    filenames = []
    for root, dirs, files_in_dir in os.walk(dir_path):
        for filename in files_in_dir:
            if filename.endswith(".dat") and not filename.endswith("MonitorFile.dat"):
                filenames.append(os.path.join(root, filename))
    return filenames


tuples_to_analyze = []
start_time = time.time()
desktop_folder = os.path.join("C:\\", "Users", "Luca Rossi", "Desktop")
folders_to_analyze = ["HCoV-229E", "MERS-CoV", "SARS-CoV", "SARS-CoV-2"]
results_folder_base = os.path.join(desktop_folder, "RESULTS")
if not os.path.exists(results_folder_base):
    os.mkdir(results_folder_base)
for fta in folders_to_analyze:
    results_folder = os.path.join(results_folder_base, fta)
    if not os.path.exists(results_folder):
        # print("Creating results folder")
        os.mkdir(results_folder)
    # else:
    #     print("Folder already exists")
    path_of_files_to_check = os.path.join(desktop_folder, "glued", "ml_data", "Cultured corona virus_I-t data", fta)
    # all folders containing relevant files to check
    all_folders_inside = os.listdir(path_of_files_to_check)
    for number_folder in all_folders_inside:
        partial_result_folder = os.path.join(results_folder, number_folder)
        specific_number_folder_to_check = os.path.join(path_of_files_to_check, number_folder)
        if not os.path.exists(partial_result_folder):
            os.mkdir(partial_result_folder)
        files = get_dat_files(specific_number_folder_to_check)
        for file_to_analyze in files:
            tuples_to_analyze.append((file_to_analyze, partial_result_folder))

files = [t[0] for t in tuples_to_analyze]
results = [t[1] for t in tuples_to_analyze]
file_numbers = list(range(len(tuples_to_analyze)))
print("Files to analyze: ", len(files))
# for f, fn, r in zip(files, file_numbers, results):
#     detect_events(f, fn, r)
with ThreadPoolExecutor(max_workers=2) as executor:
    executor.map(detect_events, files, file_numbers, results)
print(time.time() - start_time)
