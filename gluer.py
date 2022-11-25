import os
import xml.etree.ElementTree as ET
import struct
import numpy as np
import shutil


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
            raw_of_first_file, direction = merge_data_in_same_file(list_of_data_with_direction_change.pop(0), r)
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


def merge_data_in_same_file(list_of_data_with_direction_change, raw):
    raw_to_return = np.array([])
    _, last_start_position, last_direction = list_of_data_with_direction_change.pop(0)
    for _, current_start_position, current_direction in list_of_data_with_direction_change:
        raw_segment = raw[last_start_position: current_start_position]
        if last_direction == 0:
            raw_segment *= -1
        last_start_position = current_start_position
        last_direction = current_direction
        raw_to_return = np.concatenate((raw_to_return, raw_segment), axis=None)
    last_part = raw[last_start_position:]
    if last_direction == 0:
        last_part *= -1
    raw_to_return = np.concatenate((raw_to_return, last_part), axis=None)
    return raw_to_return, last_direction


def extract_raw_for_direction(data, raws, destination):
    dat_name, _ = raws[0]
    dat_name = dat_name.removesuffix(".dat")
    _, _, d1 = data[0]
    _, _, d0 = data[1]
    dat_name += "_DIRECTION_" + str(d1) + ".dat"
    raw_direction_1 = np.array([])
    data_with_direction_1 = [d for d in data if d[2] == d1]
    data_with_direction_0 = [d for d in data if d[2] == d0]
    for (f1, sp1, _), (f0, sp0, _) in zip(data_with_direction_1, data_with_direction_0):
        sp1 = int(sp1)
        sp0 = int(sp0)
        # print(sp1, sp0)
        if f1 == f0:
            raw_1 = [r[1] for r in raws if r[0] == f1].pop()
            raw_direction_1 = np.concatenate((raw_direction_1, raw_1[sp1:sp0]), axis=None)
        else:
            raw_1 = [r[1] for r in raws if r[0] == f1].pop()
            raw_0 = [r[1] for r in raws if r[0] == f0].pop()
            raw_direction_1 = np.concatenate((raw_direction_1, raw_1[sp1:], raw_0[:sp0]), axis=None)
    # because this function runs two times I don't need to catch the other case
    if len(data_with_direction_0) < len(data_with_direction_1):
        print("last section")
        _, raw = raws[-1]
        _, last_idx, _ = data[-1]
        print(last_idx)
        raw_direction_1 = np.concatenate((raw_direction_1, raw[int(last_idx):]), axis=None)
    if int(d1) == 0:
        # if direction is 0 flip the data
        raw_direction_1 = raw_direction_1 * -1
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
        data = [(rev_pos.attrib['File'], int(rev_pos.attrib['StartPosition']), int(rev_pos.attrib['Direction']))
                for rev_pos in root.iter("ReversePositionData")]
        files = {f[0] for f in data}
        files = list(sorted(files))
        raws = [(f.split(os.sep).pop(), open_dat(f)) for f in files_or_dirs if
                f.endswith(".dat") and not f.endswith("MonitorFile.dat")]
        if len(data) == 0:
            print("that's odd")
        elif len(raws) == 0:
            print("no legal files to read in dir: ", current_dir)
        # elif len(raws) != len(files):
        #     print("NOT all files in settings", current_dir)
        #     # not all files are in the settings
        #     if len(data) == 1 and len(raws) > 0:
        #         print("only one line")
        #         # the data only has one row
        #         glued_raws = np.array([])
        #         for _, raw in raws:
        #             glued_raws = np.concatenate((glued_raws, raw), axis=None)
        #         f, sp, d = data[0]
        #         dat_name, _ = raws[0]
        #         dat_name = dat_name.removesuffix(".dat") + "_DIRECTION_" + str(d) + ".dat"
        #         if int(d) == 0:
        #             glued_raws = glued_raws * -1
        #         glued_dat_path = os.path.join(destination, dat_name)
        #         with open(glued_dat_path, 'wb') as your_dat_file:
        #             your_dat_file.write(struct.pack('d' * len(glued_raws), *glued_raws))
        #     else:
        #         print("Still to manage, " + current_dir)
        #         print("Files in this dir are: ", files_or_dirs)
        #         for f, sp, d in data:
        #             print(f, sp, d)
        #         for fn, r in raws:
        #             print(fn)
        #         print(len(raws), len(files))
        else:
            improved_extraction(data, raws, destination)
            # # all files are in settings
            # print("all files in settings", current_dir)
            # if len(data) == 1:
            #     print("File only needs to be copied")
            #     # nothing to glue
            #     f, sp, d = data[0]
            #     dat_name, raw = raws[0]
            #     renamed_dat = os.path.join(destination, dat_name.removesuffix(".dat") + "_DIRECTION_" + str(d) + ".dat")
            #     if int(d) == 1:
            #         # only needs to be moved
            #         shutil.copy(dat_name, renamed_dat)
            #     else:
            #         # needs to be flipped
            #         raw = raw * - 1
            #         with open(renamed_dat, 'wb') as your_dat_file:
            #             your_dat_file.write(struct.pack('d' * len(raw), *raw))
            # else:
            #     print("first run")
            #     extract_raw_for_direction(data, raws, destination)
            #     print("second run")
            #     extract_raw_for_direction(data[1:], raws, destination)


recursive(root_dir, destination=dest)
