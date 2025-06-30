import os
import pandas as pd


def define_glob_dict(dict_of_dict):
    for key, value in dict_of_dict.items():
        globals()[key] = value
    
def define_glob_excel_file_liste(folder_name):
    files_list = []
    names = []
    for path, subdirs, files in os.walk(folder_name):
        for name in files:
            files_list.append(os.path.join(path, name))
            names.append(name.split(".")[0])
    for num, file in enumerate(files_list):
        key = names[num]
        df =  pd.read_excel(file, dtype=str)
        globals()[key] = df

def define_glob_det_dict(det_dict):
    globals()['det_dict'] = det_dict
