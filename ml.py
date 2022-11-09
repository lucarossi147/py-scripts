import numpy as np
import os
import struct
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
 
def open_dat(filename):
    f = open(filename, "rb")
    f_cont = f.read()
    f.close()
    raw = struct.unpack("d" * (len(f_cont) // 8), f_cont)
    return np.array(raw)
    
def parallel_checks(filename):
    #print(filename)
    raw = open_dat(filename)
    std_dev = np.std(raw)
    avg = np.average(raw)
    if abs(avg) > std_dev:
        return None
    bottoms = np.count_nonzero(raw < avg - (5*std_dev))
    #print(bottoms)
    if bottoms < 500:
        return None
    tops = np.count_nonzero(raw > avg + (5*std_dev))
    #print(tops)
    if tops > 10:
        return None
    return filename
    
def checks(filename):
    print(filename)
    raw = open_dat(filename)
    std_dev = np.std(raw)
    avg = np.average(raw)
    if abs(avg) > std_dev:
        return False
    bottoms = np.count_nonzero(raw < avg - (5*std_dev))
    print(bottoms)
    if bottoms < 500:
        return False
    tops = np.count_nonzero(raw > avg + (5*std_dev))
    print(tops)
    if tops > 50:
        return False
    return True
    
path_to_dir = "C:\\Users\\Luca Rossi\\Desktop\\ml_data"
#path_to_dir = "C:\\Users\\Luca Rossi\\Desktop\\ml_data\\Cultured corona virus_I-t data\\MERS-CoV"
 
filenames = []
for root, dirs, files in os.walk(path_to_dir):
    for filename in files:
        if filename.endswith(".dat") and not filename.endswith("MonitorFile.dat"):
            filenames.append(os.path.join(root, filename))
print("File to analyze: " + str(len(filenames)))
good_files=[]
 
with ThreadPoolExecutor() as executor:
    # start = time.time()
    print("RESULTS")
    results = executor.map(parallel_checks, filenames)
    good_files = [f+"\n" for f in results if f is not None]
        
#for f in filenames:
#   if checks(f):
#       good_files.append(f)
        
print("Completed Threads operations")
print("Good files are: " + str(len(good_files)))
f = open("C:\\Users\\Luca Rossi\\Desktop\\results.txt", "w")

for filename in good_files:
    try:
        f.write(filename)
    except:
        try:
            print(filename)
        except:
            print("something went wrong but could not print file name")
f.close()


# y = open_dat(good_files[0])
# plt.plot(y)
# plt.show()