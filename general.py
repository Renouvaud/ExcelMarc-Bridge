# Copyright 2025 Renouvaud
# License GPL-3.0 or later (https://www.gnu.org/licenses/gpl-3.0)

""" Python libraries """
import json
import random
import string

# Import data from a JSON file and return it as a Python object
def read_json(jsonFile):
    with open(jsonFile, encoding="utf8") as json_file:
        data = json.load(json_file)
    return data

# Open a text file and return its content as a single string
def open_as_str(file):
    with open(file, encoding="utf-8") as f_str:
        f_str = f_str.read()
    return f_str 

# Generate a random alphanumeric code of a given length (default = 4)
def create_code_alphanum(longueur=4):
    # Combination of letters and digits
    caracteres = string.ascii_letters + string.digits
    # Generate a random code
    code = ''.join(random.choice(caracteres) for _ in range(longueur))
    return code