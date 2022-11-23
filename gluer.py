import os
import xml.etree.ElementTree as ET
import struct
import numpy as np


root_dir = os.path.join("C:\\", "Users", "Luca Rossi", "Desktop", "ml_data")
dest = os.path.join("C:\\", "Users", "Luca Rossi", "Desktop", "glued")
# root_dir = os.path.join("/home", "luca", "Desktop", "ciccia", "culo")


def open_dat(filename):
    file = open(filename, "rb")
    f_cont = file.read()
    file.close()
    raw = struct.unpack("d" * (len(f_cont) // 8), f_cont)
    return np.array(raw)


def recursive(path_to_dir_or_file, destination):
    current_dir = path_to_dir_or_file.split(os.sep).pop()
    destination = os.path.join(destination, current_dir)
    if not os.path.exists(destination):
        os.mkdir(destination)
    files_or_dirs = [os.path.join(path_to_dir_or_file, fod) for fod in os.listdir(path_to_dir_or_file)]
    for fod in files_or_dirs:
        if os.path.isdir(fod):
            print(fod + " is a dir")
            recursive(fod, destination)
            return
        elif fod.endswith("Settings.xml"):
            tree = ET.parse(fod)
            root = tree.getroot()
            data = [(rev_pos.attrib['File'], rev_pos.attrib['StartPosition'], rev_pos.attrib['Direction'])
                    for rev_pos in root.iter("ReversePositionData")]
            files = {f[0] for f in data}
            files = list(sorted(files))
            raws = [(fod.split(os.sep).pop(), open_dat(fod)) for fod in files_or_dirs if
                    fod.split(os.sep).pop() in files]
            raw_direction_1 = np.array([])
            data_with_direction_1 = [d for d in data if d[2] == '1']
            data_with_direction_0 = [d for d in data if d[2] == '0']
            for (f1, sp1, d1), (f0, sp0, d0) in zip(data_with_direction_1, data_with_direction_0):
                if f1 == f0:
                    raw_1 = [r for r in raws if r[0] == f1].pop()
                    raw_direction_1 = np.concatenate((raw_direction_1, raw_1[sp1:sp0]), axis=None)
                else:
                    raw_1 = [r for r in raws if r[0] == f1].pop()
                    raw_0 = [r for r in raws if r[0] == f0].pop()
                    raw_direction_1 = np.concatenate((raw_direction_1, raw_1[sp1:], raw_0[:sp0]), axis=None)
            glued_dat_path = os.path.join(destination, 'glued.dat')
            with open(glued_dat_path, 'wb') as your_dat_file:
                your_dat_file.write(struct.pack('d' * len(raw_direction_1), *raw_direction_1))


recursive(root_dir, destination=dest)
