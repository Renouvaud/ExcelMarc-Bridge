""" Python libraries """
import xml.etree.ElementTree as ET
""" Local functions """
from complete_fields import *
from indicators import *

def create_element(record, element_list):
    record_el = ET.SubElement(record, element_list[0])
    if element_list[0] == "_comment":
        return
    record_el.text = element_list[1]

def create_control_field(row, record, control_list):
    controlfield = ET.SubElement(record, "controlfield")
    controlfield.attrib = attrib={'tag': control_list[0]}
    controlfield_list = []
    for pos in control_list[1:]:
        if pos[0] == "_comment":
            continue
        temp_val = convert_field_content(row, pos[1])
        controlfield_list.append(temp_val)
    controlfield.text = "".join(controlfield_list)

def create_fields_in_rec(row, record, map_field):
    match = re.search('([0-9]{3})[0-9_]{0,2}', map_field[0])
    # Ajout leader au record
    if map_field[0] == 'leader' or map_field[0] == 'mms_id':
        create_element(record, map_field)

    # Ajout controlfields 00X au record
    elif map_field[0].startswith("00"):
        create_control_field(row, record, map_field)

    # Ajout datafields au record
    elif match:
        tag = match.group(1)
        # traitement 'for' et 'forExcel' for multiple datafield
        is_boucle = for_eval_boucle(row, map_field[1])
        # si pas de boucle
        if not is_boucle:
            datafield = create_datafield(map_field[0])
            create_subfield(row, datafield, map_field[1:])
            if datafield.find("subfield") != None:
                map_indicator(record, datafield)
                record.append(datafield)
            return
        boucle_eval = is_boucle[0]
        sf1_list = is_boucle[1]
        boucle_type = is_boucle[2]
        boucle_excel(row, boucle_eval, sf1_list, boucle_type, tag, map_field, record, is_sf=False)
        boucle_py_dict(row, boucle_eval, sf1_list, boucle_type, tag, map_field, record, is_sf=False)
        datafields = record.findall(f"datafield[@tag='{tag}']")
        for datafield in datafields:
            map_indicator(record, datafield)
# Create holdings and items fields
def create_not_rec_field(record, balise_name):
    record_el = ET.SubElement(record, balise_name)
    return record_el