""" Python libraries """
import xml.etree.ElementTree as ET
import re

""" Local functions """
import global_dict

"""def complete_field_008(record, map_008, el_type="mono", date1="    ", date2="    ", country="fre", lang="fr"):
    c008 = ET.SubElement(record, 'controlfield')
    c008.attrib = "008"
    if el_type == "mono":
        c008.text = f"      s{date1}{date2}    {country}|||||||||| 00| 0 z{lang} d"
    return c008"""

   
def fct_split(pos, src):
    return src.split()[pos]

def secure_eval(val):
    if not val or val.strip()=='':
        return val
    return str(eval(val))

def var_substitute(row, arg):
    match = re.search('%([a-zA-Z_0-9]+)', arg)
    if not match:
        return arg
    col_name = match.group(1)
    search_el = match.group()
    return arg.replace(search_el, str(row[col_name]))      

def glob_substitute(arg):
    match = re.search('(#)[a-zA-Z_0-9]+', arg)
    if not match:
        return arg
    return arg.replace(match.group(1), "global_dict.")

def fct_if(condition, valTrue, valFalse=""):
    global last_if
    last_if = None
    if eval(condition):
        last_if = True
        return secure_eval(valTrue)    
    last_if = False
    return secure_eval(valFalse)

def fct_elif(condition, valTrue, valFalse=""):
    if last_if:
        return ""
    if eval(condition):
        return secure_eval(valTrue)
    return secure_eval(valFalse)

def convert_field_content(row, func_str):
    func_list = ["for", "if", "elif", "search", "split", "format_date","today_date"]
    mapped_value = func_str    
    if "|" in func_str:
        funcargs = func_str.split('|')
        if any(funcargs[0].startswith(func) for func in func_list):
            args = funcargs[1:]
            args = [var_substitute(row, arg) for arg in args]
            args = [glob_substitute(arg) for arg in args]
            func = "fct_" + funcargs[0]
            mapped_value = eval(func, {'fct_if':fct_if, 'fct_elif':fct_elif})(*args) #arguments donnés sous forme de liste
    return mapped_value