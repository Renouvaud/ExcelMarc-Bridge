# Copyright 2025 Renouvaud
# License GPL-3.0 or later (https://www.gnu.org/licenses/gpl-3.0)

""" Python libraries """
import xml.etree.ElementTree as ET
""" Local functions """
from complete_fields import *
from indicators import map_indicator

# Create a generic XML element inside a record
def create_element(record, element_list):
    record_el = ET.SubElement(record, element_list[0])
    # If the element is a comment, skip adding text
    if element_list[0] == "_comment":
        return
    record_el.text = element_list[1]

# Create a MARC controlfield (00X fields) and insert it into the record
def create_control_field(row, record, control_list):
    controlfield = ET.SubElement(record, "controlfield")
    controlfield.attrib = attrib={'tag': control_list[0]}
    controlfield_list = []
    for pos in control_list[1:]:
        # Ignore comments in the mapping
        if pos[0] == "_comment":
            continue
        # Convert field content based on the row values
        temp_val = convert_field_content(row, pos[1])
        controlfield_list.append(temp_val)
    # Concatenate all values into the controlfield text
    controlfield.text = "".join(controlfield_list)

# Create fields (leader, controlfields, datafields) within a MARC record
def create_fields_in_rec(row, record, map_field):
    match = re.search('([0-9]{3})[0-9_]{0,2}', map_field[0])

    # Add leader field
    if map_field[0] == 'leader':
        create_element(record, map_field)

    # Add controlfields (00X fields)
    elif map_field[0].startswith("00"):
        create_control_field(row, record, map_field)

    # Add datafields (regular MARC fields with indicators and subfields)
    elif match:
        tag = match.group(1)
        # Check if a loop condition exists ("for" or "forExcel")
        is_boucle = for_eval_boucle(row, map_field[1])
        
        # Case: no loop → create a single datafield
        if not is_boucle:
            datafield = create_datafield(map_field[0])
            create_subfield(row, datafield, map_field[1:])
            if datafield.find("subfield") != None:
                map_indicator(record, datafield)
                record.append(datafield)
            return

        # Case: loop → create multiple datafields dynamically
        boucle_eval = is_boucle[0]
        sf1_list = is_boucle[1]
        boucle_type = is_boucle[2]

        # Generate datafields either from Excel values or Python dict rules
        boucle_excel(row, boucle_eval, sf1_list, boucle_type, tag, map_field, record, is_sf=False)
        boucle_py_dict(row, boucle_eval, sf1_list, boucle_type, tag, map_field, record, is_sf=False)

        # Apply indicators to each generated datafield
        datafields = record.findall(f"datafield[@tag='{tag}']")
        for datafield in datafields:
            map_indicator(record, datafield)
            
# Create special non-record fields (holdings and items)
def create_not_rec_field(record, balise_name):
    record_el = ET.SubElement(record, balise_name)
    return record_el