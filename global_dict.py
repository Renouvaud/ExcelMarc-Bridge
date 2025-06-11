def define_glob_dict(dict_of_dict):
    for key, value in dict_of_dict.items():
        globals()[key] = value