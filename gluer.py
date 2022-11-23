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


def extract_raw_for_direction(data, raws, destination):
    dat_name, _ = raws[0]
    dat_name.removesuffix(".dat")
    _, _, d1 = data[0]
    _, _, d0 = data[1]
    dat_name += "_DIRECTION_" + str(d1) + ".dat"
    raw_direction_1 = np.array([])
    data_with_direction_1 = [d for d in data if d[2] == d1]
    data_with_direction_0 = [d for d in data if d[2] == d0]
    for (f1, sp1, _), (f0, sp0, _) in zip(data_with_direction_1, data_with_direction_0):
        sp1 = int(sp1)
        sp0 = int(sp0)
        if f1 == f0:
            raw_1 = [r[1] for r in raws if r[0] == f1].pop()
            raw_direction_1 = np.concatenate((raw_direction_1, raw_1[sp1:sp0]), axis=None)
        else:
            raw_1 = [r[1] for r in raws if r[0] == f1].pop()
            raw_0 = [r[1] for r in raws if r[0] == f0].pop()
            raw_direction_1 = np.concatenate((raw_direction_1, raw_1[sp1:], raw_0[:sp0]), axis=None)
            glued_dat_path = os.path.join(destination, dat_name)
            with open(glued_dat_path, 'wb') as your_dat_file:
                your_dat_file.write(struct.pack('d' * len(raw_direction_1), *raw_direction_1))


def recursive(path_to_dir_or_file, destination):
    current_dir = path_to_dir_or_file.split(os.sep).pop()
    destination = os.path.join(destination, current_dir)
    if not os.path.exists(destination):
        os.mkdir(destination)
    files_or_dirs = [os.path.join(path_to_dir_or_file, fod) for fod in os.listdir(path_to_dir_or_file)]
    settings_file = [fod for fod in files_or_dirs if fod.endswith("Settings.xml")]
    if len(settings_file) == 0:
        # Folder does NOT have settings.xml
        # this could be a folder of folders of a folder of files

        # call recursively this method on all sub_dirs
        [recursive(fod, destination) for fod in files_or_dirs if os.path.isdir(fod)]
    # Folder has settings.xml
    else:
        # I'm in a folder of files
        tree = ET.parse(settings_file.pop())
        root = tree.getroot()
        data = [(rev_pos.attrib['File'], rev_pos.attrib['StartPosition'], rev_pos.attrib['Direction'])
                for rev_pos in root.iter("ReversePositionData")]
        files = {f[0] for f in data}
        files = list(sorted(files))
        raws = [(f.split(os.sep).pop(), open_dat(f)) for f in files_or_dirs if
                f.endswith(".dat") and not f.endswith("MonitorFile.dat")]
        if len(raws) != len(files):
            print("NOT all files in settings", current_dir)
            # not all files are in the settings
        else:
            # all files are in settings
            print("all files in settings", current_dir)
            extract_raw_for_direction(data, raws, destination)
            extract_raw_for_direction(data[1:], raws, destination)


recursive(root_dir, destination=dest)
