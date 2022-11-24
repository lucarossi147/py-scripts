import csv
import struct
import numpy as np
import matplotlib.pyplot as plt
import os


def extract_lengths(filename):
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        event_positions = []
        for row in csv_reader:
            if len(row) > 1:
                if line_count > 1:
                    if len(row) == 2:
                        event_positions.append((int(row[0]), int(row[0])))
        return event_positions


def open_dat(filename):
    file = open(filename, "rb")
    f_cont = file.read()
    file.close()
    raw = struct.unpack("d" * (len(f_cont) // 8), f_cont)
    return np.array(raw)


def plot_stuff(dat_file, csv_file):
    raw = open_dat(dat_file)
    event_positions = extract_lengths(csv_file)
    events = np.zeros(raw.shape)
    for s, e in event_positions:
        events = np.concatenate((events[:s], np.ones(events[s:e]), events[e:]), axis=None)
    plt.plot(events)
    plt.plot(raw)
    plt.show()


root_dir = os.path.join("C:\\", "Users", "Luca Rossi", "Desktop", "RESULTS", "HCoV-229E", "20200622154659",
                        "NK-2-1-1st-FIL_001_DIRECTION_0")
plot_stuff(os.path.join(root_dir, "NK-2-1-1st-FIL_001_DIRECTION_0.dat"), os.path.join(root_dir, "details.csv"))
