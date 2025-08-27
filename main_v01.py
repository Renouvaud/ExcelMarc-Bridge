# Copyright 2025 Renouvaud
# License GPL-3.0 or later (https://www.gnu.org/licenses/gpl-3.0)

""" Python libraries """
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import *
import os
import re

""" Local functions """
from general import read_json
from global_dict import *
from fields_in_rec import create_fields_in_rec, create_subfield, create_not_rec_field
from complete_fields import add_subfield
import global_dict


if __name__ == "__main__":
    print("-------------------------------------------")
    start = datetime.now()
    print(f"Start time : {start.strftime('%d-%m-%Y %H:%M:%S')}")
    print("-------------------------------------------")
    print("-------------------------------------------")
    log_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Import json params file
    ###################################################
    # Update next line with new gen_params.json name  #
    ###################################################
    gen_param_file = "gen_params"
    ###################################################
    gen_params = read_json(f"./{gen_param_file}.json")
    mapping = gen_params['mapping']

    # Import additional dictionaries
    glob_dict = gen_params['global_dict']
    define_glob_dict(glob_dict)

    # Import additional Excel files from folder
    folder = gen_params['xlsx_folder']
    define_glob_excel_file_liste(folder)

    # Import det for 245 indicators
    det_dict = read_json("./ind245.json")
    define_glob_det_dict(det_dict)

    # Define output XML file name
    xml_output_file = f"{gen_params['xml_file_output']}.xml"

    # Define input Excel file path
    xlsx_f_name = f"{gen_params['xlsx_file_input']}.xlsx"
    excel_file = os.path.join(os.getcwd(), xlsx_f_name)

    # Open Excel file into a pandas DataFrame
    df = pd.read_excel(excel_file, dtype=str)

    # Create the root XML element <collection>
    collection = ET.Element('collection', {
        'xmlns:marc': "http://www.loc.gov/MARC21/slim",
        'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance"
    })
    
    # For each row in the Excel file, create a <record>
    print("Input file column name, value, and format")
    print("-------------------------------------------")
    printed_col = []
    num = 0
    for _, row in df.iterrows():
        num +=1
        record = ET.SubElement(collection, 'record')

        # Replace special characters (#, @) defined in gen_params.json
        for row_key, row_val in row.items():
            if type(row_val)==str and re.search("[#@]", row_val):
                row_val = row_val.replace("#", "<diese>")
                row_val = row_val.replace("@", "<at>")
                row[row_key] = row_val

            # Print the column name and value once if not already printed
            if row_key not in printed_col and row_val != None and str(row_val).lower().strip() not in ["nan", ""]:
                print(f"{row_key}\t\t{row_val}\t\t{type(row_val)}")
                printed_col.append(row_key)

        # For each element in the mapping list defined in the JSON config
        for map_field in mapping:
            # Add MMS ID if it exists
            if 'mms_id' == map_field[0]:
                add_subfield(record, row, map_field[0], map_field[1], is_datafield=False)

            # Add leader, controlfield, and datafield with subfields
            create_fields_in_rec(row, record, map_field)

            # Add holding section to record if defined
            if 'holding_data' == map_field[0]:
                record_el = create_not_rec_field(record, map_field[0])
                for map_el in map_field[1:]:
                    create_fields_in_rec(row, record_el, map_el)

            # Add item section to record if defined
            if 'item_data' == map_field[0]:
                record_el = create_not_rec_field(record, map_field[0])
                create_subfield(row, record_el, map_field[1:], is_datafield=False)

        # Log progress at specific intervals
        if num in [1, 10, 100]:
            print(f"line {num} processed")
        elif num % 500 == 0:
            print(f"processing still in progress, line {num} processed")

    # Generate and write the final XML file
    tree = ET.ElementTree(collection)
    ET.indent(tree, space="   ", level=0)
    tree.write(xml_output_file, encoding="utf-8", xml_declaration=True)