import os
import csv
import struct
import numpy as np
import math
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt

def open_dat(filename):
    f = open(filename, "rb")
    f_cont = f.read()
    f.close()
    raw = struct.unpack("d" * (len(f_cont) // 8), f_cont)
    return np.array(raw)

def extract_lengths(filename):
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        events_lengths = []
        for row in csv_reader:
            if len(row) > 1:
                if line_count > 2:
                    events_lengths.append(int(row[1]) - int(row[0]))
            line_count+=1
        return events_lengths

def analyze(dir_name):
    stereotype_length = 35
    files = os.listdir(dir_name)
    experiment_name = dir_name
    dat_file = [dir_name + os.sep + f for f in files if f.endswith(".dat")].pop()
    details_file = [dir_name + os.sep + f for f in files if f.endswith(".csv")].pop()
    
    # caricamento eventi dal singolo file    
    events = open_dat(dat_file)
    # caricamento dettagli file
    events_length = extract_lengths(details_file)

    good_events_n = 0
    event_avg = np.zeros(34)
    b = 0
    # ciclo sulle lunghezze degli eventi
    for ev_len in events_length:
        # scarto eventi troppo brevi
        if ev_len < 30:
            continue
        e = b + ev_len
        event = events[b:e]
        b = e

        # calcolo la baseline sul primo 20% del primo terzo dei dati e
        # sull'ultimo 20% dell'ultimo terzo dei dati
        x_baseline = np.concatenate((event[:round(ev_len/3*0.2)], event[round(ev_len - ev_len/3*0.2):]))
        baseline = np.mean(x_baseline)
        amplitude = baseline - event.min()
        event_50 = np.nonzero(event < baseline - amplitude / 2)[0]
        # istante in cui l'evento supera il 50% dell'escursione
        b50 = event_50[0]
        # istante in cui l'evento torna al di sotto del 50% dell'escursione
        e50 = event_50[-1]
        d50 = e50 - b50  
        # faccio il logaritmo di ampiezze e durate perchè gli istogrammi in
        # scala logaritmica sono più simmetrici

        # inoltre faccio un whitening semplificato: sottraggo la media e
        # divido per la deviazione standard calcolate in un'esecuzione precedente
        SA = (math.log(amplitude)+21.175012761120229)/0.412530189443423
        SD = (math.log(d50)-3.982651178110859)/1.020579064361968

        SF.append(math.sqrt(pow(SA,2)+pow(SD,2)))
        # forma d'onda normalizzata:
        # in ampiezza dividendo per amplitude
        # in durata facendo la spline su un numero fisso di campioni
        x = [x for x in range(ev_len)]
        x_norm = np.linspace(0, ev_len-1, stereotype_length*3+4)
        f = CubicSpline(x, event/amplitude)
        event_norm = f(x_norm)
        event_norm = event_norm[stereotype_length+3:2*stereotype_length+2]
        # SW.append(math.sqrt(np.sum(event_norm)))

        amplitudes.append(amplitude)
        d50s.append(d50)
        event_avg += event_norm
        good_events_n+=1
        # plt.plot(event_norm)
        # plt.show()

    return event_avg, good_events_n

    # event_avg = event_avg / good_events_n


good_events_tot = 0
event_stereotype = np.zeros(34)
SF = []
SW = []
amplitudes = []
d50s = []
root_folder = r"/home/luca/Desktop/extracted events"
# root_folder = os.path.join("C:\\","Users", "Luca Rossi", "Desktop","extracted events")
event_folders = [root_folder + os.sep + d for d in os.listdir(root_folder)]

for event in event_folders:
    event_avg, good_events_n = analyze(event)
    event_stereotype += event_avg
    good_events_tot += good_events_n


event_stereotype = event_stereotype / good_events_tot
log_amplitudes = np.log(amplitudes)
print(np.mean(log_amplitudes), np.std(log_amplitudes))
log_d = np.log(d50s)
print(np.mean(log_d), np.std(log_d))

# plt.plot(event_stereotype)
# plt.loglog(amplitudes, d50s, 'o')
# plt.hist(np.log(amplitudes))
# plt.show()
