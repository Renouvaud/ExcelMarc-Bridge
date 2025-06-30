""" Local functions """
from asyncio.windows_events import NULL
from queue import Empty
from general import *
#from complete_fields import *
from global_dict import *
import global_dict
from fields_in_rec import *

""" Python libraries """
import pandas as pd
import json
import xml.etree.ElementTree as ET
from datetime import *
import os
from os import listdir #, walk
from os.path import isfile, isdir, join
import re

# Calls function main()
if __name__ == "__main__":
    
    # Démarrage du calcul de la durée d'exécution du programme
    start = datetime.now()
    print(f"Start time : {start.strftime('%d-%m-%Y %H:%M:%S')}")
    log_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Import json params file
    gen_param_file = "gen_params"
    gen_params = read_json(f"./{gen_param_file}.json")
    mapping = gen_params['mapping']

    # Import des dictionnaires complémentaires
    glob_dict = gen_params['global_dict']
    define_glob_dict(glob_dict)

    # Import des fichiers complémentaires
    folder = gen_params['xlsx_folder']
    define_glob_excel_file_liste(folder)

    # Import det pour ind 245
    det_dict = read_json("./ind245.json")
    define_glob_det_dict(det_dict)

    # Import nom fichier de sortie
    xml_output_file = f"{gen_params['xml_file_output']}.xml"

    # Import fichier excel
    xlsx_f_name = f"{gen_params['xlsx_file_input']}.xlsx"
    excel_file = os.path.join(os.getcwd(), xlsx_f_name)
    # Ouverture fichier excel
    df = pd.read_excel(excel_file, dtype=str)

    # Créer la racine XML
    collection = ET.Element('collection', {
        'xmlns:marc': "http://www.loc.gov/MARC21/slim",
        'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance"
    })
    # Pour chaque ligne du fichier excel, création d'un record
    printed_col = []
    num = 0
    for _, row in df.iterrows():
        num +=1
        record = ET.SubElement(collection, 'record')
        # Remplacement des carctères spéciaux utilisés dans gen_params.json dans la ligne traitée
        for row_key, row_val in row.items():
            if type(row_val)==str and re.search("[#@]", row_val):
                row_val = row_val.replace("#", "<diese>")
                row_val = row_val.replace("@", "<at>")
                row[row_key] = row_val
            if row_key not in printed_col and row_val != None and str(row_val).lower().strip() not in ["nan", ""]:
                print(f"{row_key}\t\t{row_val}\t\t{type(row_val)}")
                printed_col.append(row_key)

        # Pour chaque élément de la liste mapping définie dans le fichier json
        for map_field in mapping:

            #cration leader, controlfiel et datafield with subfield
            create_fields_in_rec(row, record, map_field)

            # Ajout holding au record
            if 'holding_data' == map_field[0]:
                record_el = create_not_rec_field(record, map_field[0])
                for map_el in map_field[1:]:
                    create_fields_in_rec(row, record_el, map_el)
            # Ajout item au record
            if 'item_data' == map_field[0]:
                record_el = create_not_rec_field(record, map_field[0])
                create_subfield(row, record_el, map_field[1:], is_datafield=False)
        if num in [1, 10, 100]:
            print(f"ligne {num} traitée")
        elif num % 500 == 0:
            print("traitement toujours en cours, ligne {num} traitée")
    # Génération du fichier XML
    tree = ET.ElementTree(collection)
    ET.indent(tree, space="   ", level=0)  # Pour Python 3.9+
    tree.write(xml_output_file, encoding="utf-8", xml_declaration=True)