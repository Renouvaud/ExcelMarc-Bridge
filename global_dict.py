# Copyright 2025 Renouvaud
# License GPL-3.0 or later (https://www.gnu.org/licenses/gpl-3.0)

import os
import pandas as pd

# Load a dictionary of dictionaries into global variables
def define_glob_dict(dict_of_dict):
    for key, value in dict_of_dict.items():
        globals()[key] = value

# Load all Excel files from a folder into global variables
def define_glob_excel_file_liste(folder_name):
    files_list = []
    names = []
    # Walk through the folder and collect all file paths
    for path, subdirs, files in os.walk(folder_name):
        for name in files:
            files_list.append(os.path.join(path, name))
            names.append(name.split(".")[0]) # Use filename (without extension) as key
    
    # Read each Excel file into a DataFrame and store in globals           
    for num, file in enumerate(files_list):
        key = names[num]
        df =  pd.read_excel(file, dtype=str)
        globals()[key] = df
        
# Store the det_dict dictionary as a global variable
def define_glob_det_dict(det_dict):
    globals()['det_dict'] = det_dict
