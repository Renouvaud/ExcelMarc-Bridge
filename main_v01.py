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

    xlsx_f_name = f"{gen_params['xlsx_file_input']}.xlsx"
    excel_file = os.path.join(os.getcwd(), xlsx_f_name)

    # Import nom fichier de sortie
    xml_output_file = f"{gen_params['xml_file_output']}.xml"

    # Ouverture fichier excel
    df = pd.read_excel(excel_file)

    # Créer la racine XML
    collection = ET.Element('collection', {
        'xmlns:marc': "http://www.loc.gov/MARC21/slim",
        'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance"
    })

    for _, row in df.iterrows():
        record = ET.SubElement(collection, 'record')
        """leader = ET.SubElement(record, 'leader')
        leader.text = '00000nam a2200000   4500'

        fields_by_tag = {}

        # Regroupement des sous-champs par tag
        for col, val in row.items():
            if pd.notnull(val) and col in mapping.keys():
                tag_code = mapping[col]  # e.g. "245_a"
                tag, code = tag_code.split('_')
                fields_by_tag.setdefault(tag, []).append((code, str(val)))"""
        for map_field in mapping:

            # ajout leader au record
            if not isinstance(map_field[1], list):
                record_el = ET.SubElement(record, map_field[0])
                record_el.text = map_field[1]

            # ajout controlfields 00X au record
            elif map_field[0].startswith("00"):
                controlfield = ET.SubElement(record, "controlfield")
                controlfield.attrib = attrib={'tag': map_field[0]}
                controlfield_list = []
                for pos in map_field[1:]:
                    temp_val = convert_field_content(row, pos[1])
                    controlfield_list.append(temp_val)
                controlfield.text = "".join(controlfield_list)

            # ajout datafields
            match_tag = re.search('([0-9]{3})(([0-9_#])([0-9_#]))?')
            elif re.search('[0-9]{3}[0-9_#]{0,2}', map_field[0]):
                b

                
        # Ajout des datafields
        """for tag, subfields in fields_by_tag.items():
            datafield = ET.Element('datafield', attrib={'tag': tag, 'ind1': ' ', 'ind2': ' '})
            for code, value in subfields:
                sf = ET.SubElement(datafield, 'subfield', attrib={'code': code})
                sf.text = value
            record.append(datafield)"""

    # Génération du fichier XML
    tree = ET.ElementTree(collection)
    ET.indent(tree, space="   ", level=0)  # Pour Python 3.9+
    tree.write(xml_output_file, encoding="utf-8", xml_declaration=True)