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


def improved_extraction(data, raws, destination):
    files_from_data = {f[0] for f in data}
    files_from_data = list(sorted(files_from_data))

    raw_direction_1 = np.array([])
    # controllare sempre che ci sia un elemento prima di poppare
    list_of_data_with_direction_change = []
    for f in files_from_data:
        data_with_direction_change = [d for d in data if d[0] == f]
        list_of_data_with_direction_change.append(data_with_direction_change)
    last_direction = 0
    f_name = files_from_data.pop(0)
    for f, r in raws:
        if f == f_name:
            raw_of_first_file, direction = merge_data_in_same_file(list_of_data_with_direction_change.pop(0), r,
                                                                   last_direction)
            last_direction = direction
            raw_direction_1 = np.concatenate((raw_direction_1, raw_of_first_file), axis=None)
            if len(files_from_data) > 0:
                f_name = files_from_data.pop(0)
        else:
            if last_direction == 0:
                r *= -1
            raw_direction_1 = np.concatenate((raw_direction_1, r), axis=None)
    dat_name, _ = raws[0]
    glued_dat_path = os.path.join(destination, dat_name)
    with open(glued_dat_path, 'wb') as your_dat_file:
        your_dat_file.write(struct.pack('d' * len(raw_direction_1), *raw_direction_1))


def merge_data_in_same_file(list_of_data_with_direction_change, raw, direction):
    raw_to_return = np.array([])
    _, last_start_position, last_direction = list_of_data_with_direction_change.pop(0)
    first_part = raw[:last_start_position]
    raw_to_return = adjust_and_concat(raw_to_return, first_part, direction)
    for _, current_start_position, current_direction in list_of_data_with_direction_change:
        raw_segment = raw[last_start_position: current_start_position]
        raw_to_return = adjust_and_concat(raw_to_return, raw_segment, last_direction)
        last_start_position = current_start_position
        last_direction = current_direction
    last_part = raw[last_start_position:]
    raw_to_return = adjust_and_concat(raw_to_return, last_part, last_direction)
    return raw_to_return, last_direction


def adjust_and_concat(base_raw, raw_to_concat, direction):
    if direction == 0:
        raw_to_concat *= -1
    return np.concatenate((base_raw, raw_to_concat), axis=None)


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
        data = [(rev_pos.attrib['File'], int(rev_pos.attrib['StartPosition']), int(rev_pos.attrib['Direction']))
                for rev_pos in root.iter("ReversePositionData")]
        raws = [(f.split(os.sep).pop(), open_dat(f)) for f in files_or_dirs if
                f.endswith(".dat") and not f.endswith("MonitorFile.dat")]
        if len(data) == 0:
            print("that's odd")
        elif len(raws) == 0:
            print("no legal files to read in dir: ", current_dir)
        else:
            improved_extraction(data, raws, destination)


recursive(root_dir, destination=dest)
