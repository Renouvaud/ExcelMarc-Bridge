""" Local functions """
from general import *
from complete_fields import *
from global_dict import *

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
    glob_dict = gen_params['global_dict']
    define_glob_dict(glob_dict)

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
    for _, row in df.iterrows():
        record = ET.SubElement(collection, 'record')

        # Remplacement des carctères spéciaux utilisés dans gen_params.json dans la ligne traitée
        for row_key, row_val in row.items():
            if type(row_val)==str and re.search("[#@]", row_val):
                row_val = row_val.replace("#", "<diese>")
                row_val = row_val.replace("@", "<at>")
                row[row_key] = row_val
            if row_key not in printed_col and row_val not in ["nan", "", None, nan, 0]:
                print(f"{row_key}\t\t{row_val}")
                printed_col.append(row_key)

        # Pour chaque élément de la liste mapping définie dans le fichier json
        for map_field in mapping:

            # Ajout leader au record
            if not isinstance(map_field[1], list):
                record_el = ET.SubElement(record, map_field[0])
                record_el.text = map_field[1]

            # Ajout controlfields 00X au record
            elif map_field[0].startswith("00"):
                controlfield = ET.SubElement(record, "controlfield")
                controlfield.attrib = attrib={'tag': map_field[0]}
                controlfield_list = []
                for pos in map_field[1:]:
                    if pos[0] == "_comment":
                        continue
                    temp_val = convert_field_content(row, pos[1])
                    controlfield_list.append(temp_val)
                controlfield.text = "".join(controlfield_list)

            # Ajout datafields au record
            elif re.search('[0-9]{3}[0-9_#]{0,2}', map_field[0]):
                match_tag = re.search('([0-9]{3})(([0-9_#])([0-9_#]))?', map_field[0])
                tag = match_tag.group(1)
                ind1 = get_ind(match_tag.group(3))
                ind2 = get_ind(match_tag.group(4))
                datafield = ET.Element('datafield', attrib={'tag': tag, 'ind1': ind1, 'ind2': ind2})

                for sf in map_field[1:]:
                    if sf[0] == "_comment":
                        continue
                    if sf[1].startswith("for§"):
                        # exemple de sf avec for : ["a", "for§'@Langue'.split('/')§if§%s in #lang008.keys§#lang008[%s]"]
                        # sf[1] = "for§'@Langue'.split('/')§if§%s in #lang008.keys§#lang008[%s]"
                        sf1_list = sf[1].split('§') # = "for", "'@Langue'.split('/')", "if", "%s in #lang008.keys§#lang008[%s]"
                        boucle = sf1_list[1] # = '@Langue'.split('/')
                        mapped_value = map_value(row, sf1_list[1], cond_var=True, cond_glob=True) # = 'EN/FR/DE'.split('/')
                        # cette boucle permet de créer plusieurs sous-champs avec le même code en bouclant sur une liste
                        # exemple : 041 $a eng $a fre $a ger
                        for el in eval(mapped_value):
                            if el == None or el == '':
                                continue
                            if len(sf1_list)<2:
                                message_erreur_for(tag, sf)
                                exit()
                            func_str = "§".join(sf1_list[2:])
                            add_subfield(datafield, row, sf[0], func_str.replace("%s", f"'{el}'"))
                    else:
                        add_subfield(datafield, row, sf[0], sf[1])
                record.append(datafield)            
            #ET.dump(record)

    # Génération du fichier XML
    tree = ET.ElementTree(collection)
    ET.indent(tree, space="   ", level=0)  # Pour Python 3.9+
    tree.write(xml_output_file, encoding="utf-8", xml_declaration=True)