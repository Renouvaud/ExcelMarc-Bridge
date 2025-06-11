""" Python libraries """
import json
import re
import random
import string

# import data of json file
def read_json(jsonFile):
    with open(jsonFile, encoding="utf8") as json_file:
        data = json.load(json_file)
    return data

def open_as_str(file):
    with open(file, encoding="utf-8") as f_str:
        f_str = f_str.read()
    return f_str 

def create_code_alphanum(longueur=4):
    # Combinaison de lettres et de chiffres
    caracteres = string.ascii_letters + string.digits
    # Générer un code aléatoire
    code = ''.join(random.choice(caracteres) for _ in range(longueur))
    return code

"""def normalize_key(key):
    key = key.lower()
    key = re.sub(r'[^a-z0-9_]', '_', key)
    key = key.replace(' ', '_')
    return key"""

"""def reduce_list(original_list):
    seen = set() # Ensemble pour suivre les valeurs déjà rencontrées
    return {v for v in original_list if not (v in seen or seen.add(v))}"""