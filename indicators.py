# Copyright 2025 Renouvaud
# License GPL-3.0 or later (https://www.gnu.org/licenses/gpl-3.0)

""" Local functions """
import global_dict

def get_ind(check_str):
    if check_str != None:
        return check_str
    return ' '

def empty_ind(ind, datafield):
    indx = datafield.attrib[ind]
    if ' ' != indx:
        return indx.replace("_", " ")
    return

def find_sf(datafield, code):
    sf = datafield.find(f"subfield[@code='{code}']")
    if sf != None:
        return
    return sf.text

def map_ind245(record, datafield):
    ind2 = "0"
    lang_traitees = ["fre", "ger", "eng", "ita", "mul"]
    c008lang = record.find("controlfield[@tag='008']").text
    lang008 = c008lang[-5:-2]
    f245a = datafield.find("subfield[@code='a']")
    if f245a != None:
        f245a = f245a.text
        det_dict  = global_dict.det_dict
        if lang008 in lang_traitees:
            for lang, det_list in det_dict.items():
                if lang008 != lang and lang008 != "mul":
                    continue
                for det in det_list:
                    if f245a.startswith(det):
                        ind2 = str(len(det))
                        break
            datafield.set('ind2', ind2)
    f100a = record.find("datafield[@tag='100']/subfield[@code='a']")        
    if f100a != None:
        ind1 = "1"
    else:
        ind1 = "0"
    datafield.set('ind1', ind1)       
    return

def map_ind_aut(datafield):
    f_aut = datafield.find("subfield[@code='a']")        
    if f_aut != None and "," in f_aut.text:
        datafield.set('ind1', "1")
    else:
        datafield.set('ind1', "0")
    datafield.set('ind2', " ")

def map_ind_700(datafield):
    f_aut = datafield.find("subfield[@code='a']")
    if f_aut != None and "famille" in f_aut.text.lower():
        datafield.set('ind1', "3")
    else:
        map_ind_aut(datafield)
    f_titre = datafield.find("subfield[@code='t']")
    if f_titre != None:
        datafield.set('ind2', "2")

def map_ind_600(datafield):
    map_ind_aut(datafield)
    datafield.set('ind2', "7")

def map_ind_630(datafield):
    datafield.set('ind1', "0")
    datafield.set('ind2', "7")

def map_ind_650(datafield):
    datafield.set('ind1', " ")
    datafield.set('ind2', "7")

def map_ind_655(datafield):
    datafield.set('ind1', " ")
    datafield.set('ind2', "7")

def map_indicator(record, datafield):
    tag_list = ['100', '700', '600', '630', '650', '655', '245']
    tag = datafield.attrib['tag']
    ind1 = empty_ind('ind1', datafield)
    ind2 = empty_ind('ind2', datafield)
    if ind1 and ind2:
        datafield.set('ind1', ind1)
        datafield.set('ind2', ind2)
        return
    if tag not in tag_list:
        return
    if tag == '245':
        map_ind245(record, datafield)
    elif tag == '100':
        map_ind_aut(datafield)
    elif tag == '700' :
        map_ind_700(datafield)
    elif tag == '600' :
        map_ind_600(datafield)
    elif tag == '630' :
        map_ind_630(datafield)
    elif tag == '650' :
        map_ind_650(datafield)
    elif tag == '655' :
        map_ind_655(datafield)
         
