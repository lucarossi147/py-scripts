from filesplit.split import Split
import os

MAX_FILE_LENGTH = 16777216 * 8
root_dir = os.path.join("C:\\", "Users", "Luca Rossi", "Desktop", "ml_data_splitted")


def recursive(path_to_dir_or_file):
    files_or_dirs = [os.path.join(path_to_dir_or_file, fod) for fod in os.listdir(path_to_dir_or_file)]
    for fod in files_or_dirs:
        if os.path.isdir(fod):
            print(fod + " is a dir")
            recursive(fod)
        elif fod.endswith(".dat"):
            print(fod + " is a dat file")
            if os.path.getsize(fod) > MAX_FILE_LENGTH:
                print("file " + fod + " is too large")
                Split(fod, path_to_dir_or_file).bysize(MAX_FILE_LENGTH)
                os.remove(fod)


recursive(root_dir)
