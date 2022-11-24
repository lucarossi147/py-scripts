import os
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


def glue(files):
    raws = [open_dat(f) for f in files]
    new_raw = np.array([])
    for r in raws:
        new_raw = np.concatenate((new_raw, r), axis=None)
    fname = files[0].split(os.sep).pop()
    glued_dat_path = os.path.join(dest, fname)
    with open(glued_dat_path, 'wb') as your_dat_file:
        your_dat_file.write(struct.pack('d' * len(new_raw), *new_raw))


filenames = []
glue([os.path.join(root_dir, f) for f in filenames])
