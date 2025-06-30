""" Python libraries """
from cmath import nan
from multiprocessing import Value
import xml.etree.ElementTree as ET
import re
from datetime import datetime
from indicators import *

""" Local functions """
import global_dict

def rpl_json_spe_caracter(ET_el):
    ET_el = ET_el.replace("<diese>", "#")
    ET_el = ET_el.replace("<at>", "@")
    return ET_el

def convert_space_caracter(val, replacement, reg_rpl, not_inc={}):
    if len(not_inc)>0:
        val = re.sub(" *[\n\t\r] *", replacement, val)
        for not_search, not_rpl in not_inc.items():
            val = re.sub(f"{not_search}{reg_rpl}", f"{not_rpl} ", val)
    else:
        val = re.sub(" *[\n\t\r] *", replacement, val)
    val = re.sub(reg_rpl, replacement, val)
    val = re.sub(f"^{reg_rpl}", "", val)
    val = re.sub(f"{reg_rpl}$", "", val)
    return val

def convert_special_caracter(val, spe_car_list, remplacement):
    for spe_car in spe_car_list:
        match_spe = re.search(f"{spe_car}", val)
        if match_spe != None:
            val = val.replace(match_spe.group(), remplacement)
    return val

def var_substitute(row, arg, cond=False):
    list_arg = []
    list_arg.append(arg.split("@")[0])
    if len(arg.split("@"))>1:
        for mot in arg.split("@")[1:]:
            mot = f"@{mot}"
            match = re.search("@([a-zA-Z_0-9]+)", mot)
            col_name = f"{match.group(1)}"
            search_el = match.group()
            col_val = str(row[col_name])
            if col_val == 'nan':
                col_val = ''
            # Remplacement de " par ' --> toujours même délémitations pour citation
            col_val = convert_special_caracter(col_val, ['"'], "'")
            # Remplacement des retours à la ligne et tab en fonction de la colonne
            if re.search("(contenu)|(505)", col_name.lower()) and not col_val.startswith("[Sommaire]"):
                col_val = convert_space_caracter(col_val, " -- ", "( -- )+")
            elif re.search("r[éeè]sum[éeè]r?", col_name.lower()) or (re.search("som+aire", col_name.lower()) and col_val.startswith("[Sommaire]")):
                col_val = convert_space_caracter(col_val, " - ", "( - )+")
            else :
                col_val = convert_space_caracter(col_val, ". ", "(\. )+", not_inc={"\?":"?", "\.":".", "!":"!", ":":":", ",":",", ";":";"})            
            if cond:
                # Pour condition attention à remplace les citations dans les données
                col_val = convert_special_caracter(col_val, ["'"], " ")
                list_arg.append(mot.replace(search_el, f"'{col_val}'"))
            else:
                list_arg.append(mot.replace(search_el, col_val))
    return "".join(list_arg)  

def glob_eval(el):
    if not el:
        return el
    m_guillemet = re.search("global_dict\.[a-zA-Z_0-9]+(\[)[a-zA-Z_0-9\.,_\-]+(\])", el)
    if m_guillemet:
        el = el.replace(m_guillemet.group(1), "['")
        el = el.replace(m_guillemet.group(2), "']")
    match = re.search("global_dict\.[a-zA-Z_0-9]+((\['[a-zA-Z_0-9\.,_\-]+'\])|(\.((keys)|(values)|(items))\(\)))?", el)
    if not match:
        return el
    try:
      return el.replace(match.group(), str(eval(match.group())))    
    except:
        print("Erreur : impossible d'accéder à la variable globale")
        print(f"Vérifier le fichier json pour : {el}")
        exit()

def glob_substitute(arg, cond=False):
    list_arg = []
    list_arg.append(arg.split("#")[0])
    if len(arg.split("#"))>1:
        for mot in arg.split("#")[1:]:
            mot = f"global_dict.{mot}"
            if cond:
                list_arg.append(mot)
            else:
                mot = glob_eval(mot)
                list_arg.append(mot)
                #match = re.search("global_dict\.[a-zA-Z_0-9]+((\['[a-zA-Z_0-9,]+'\])|(\.((keys)|(values)|(items))\(\)))?", mot)
                #list_arg.append(mot.replace(match.group(), str(eval(match.group()))))
            #match = re.search('(#)[a-zA-Z_0-9]+', mot)
            #list_arg.append(mot.replace(match.group(1), "global_dict."))
    return "".join(list_arg)

def fct_if(condition, valTrue, valFalse=""):
    global last_if
    last_if = None
    if eval(condition):
        last_if = True
        return glob_eval(valTrue)    
    last_if = False
    return glob_eval(valFalse)

def fct_elif(condition, valTrue, valFalse=""):
    global last_if
    if last_if:
        return ""
    if eval(condition):
        last_if = True
        return glob_eval(valTrue)
    return glob_eval(valFalse)

"""def fct_search():
    pass

def fct_format_date():
    pass

def fct_today_date():
    pass

def fct_split(pos, src):
    return src.split()[pos]"""

def map_value(row, value, cond_var=False, cond_glob=False):
    mapped_value = var_substitute(row, value, cond_var)
    mapped_value = glob_substitute(mapped_value, cond_glob)
    return mapped_value

def apply_fct(row, funcargs, value):
    func_list = ["if", "elif"] 
    if any(funcargs[0].startswith(func) for func in func_list):
        arg_list = []
        arg_list.append(map_value(row, funcargs[1], cond_var=True, cond_glob=True))
        [arg_list.append(map_value(row, arg, cond_var=False, cond_glob=True)) for arg in funcargs[2:]]
        func = "fct_" + funcargs[0]
        #'fct_if':fct_if, 'fct_elif':fct_elif, 'fct_search':fct_search, 'fct_split':fct_split, 'fct_format_date':fct_format_date, 'fct_today_date':fct_today_date
        return eval(func, {'fct_if':fct_if, 'fct_elif':fct_elif})(*arg_list) #arguments donnés sous forme de liste
    return map_value(row, value)

def convert_date(date_str, d_format_entree, d_format_sortie):
    # Convertir la chaîne en objet datetime
    try:
        date_obj = datetime.strptime(date_str, d_format_entree)
    except:
        return ""
    # Changer le format en DD.MM.YYYY
    try :
        date_formatee = date_obj.strftime(d_format_sortie)
    except:
        return ""
    return date_formatee

def fct_format_date(row, content, reg_date):
    m_format_date = re.search(f"format_date\((@[a-zA-Z0-9_]+), ?({reg_date}), ?({reg_date})\)", content)
    if not m_format_date:
        print("Erreur dans format_date")
        print("ex : format_date(@col_name, <format date entrée>, <format date sortie>)")
        print("exemple : format_date(@Date_achat, %a %b %d %H:%M:%S %Z %Y, %Y-%m-%d)")
        print("détails des formats de date\n%a : Jour de la semaine abrégé (ex. : Mon)\n%b : Mois abrégé (ex. : Nov)\n%d : Jour du mois (ex. : 01)\n%H : Heure (format 24 heures, ex. : 00)\n%M : Minutes (ex. : 00)\n%S : Secondes (ex. : 00)\n%Z : Fuseau horaire (ex. : CET)\n%Y : Année avec siècle (ex. : 1993)")
        exit()
    value = var_substitute(row, m_format_date.group(1), cond=False)
    new_date = convert_date(value, m_format_date.group(2), m_format_date.group(3))
    return content.replace(m_format_date.group(), new_date)

def fct_today_date(content, reg_date):
    m_format_date = re.search(f"today_date\(({reg_date})\)", content)
    if not m_format_date:
        print("Erreur dans today_date")
        print("ex : today_date(<format date>)")
        print("exemple : today_date(%m.%Y)")
        print("détails des formats de date\n%a : Jour de la semaine abrégé (ex. : Mon)\n%b : Mois abrégé (ex. : Nov)\n%d : Jour du mois (ex. : 01)\n%H : Heure (format 24 heures, ex. : 00)\n%M : Minutes (ex. : 00)\n%S : Secondes (ex. : 00)\n%Z : Fuseau horaire (ex. : CET)\n%Y : Année avec siècle (ex. : 1993)")
        exit()
    try:
        new_date = datetime.now().strftime(m_format_date.group(1))
    except:
        return "Erreur today_date ; format date en entrée invalide"        
    return content.replace(m_format_date.group(), new_date)

def convert_field_content(row, func_str):
    fct_date_list = ["format_date","today_date"]
    for fct_date in fct_date_list:
        if fct_date in func_str:
            reg_date = "[%abdHMSZYym\.\-:_ ]+"
            if fct_date == "format_date":
                func_str = fct_format_date(row, func_str, reg_date)
            elif fct_date == "today_date":
                func_str = fct_today_date(func_str, reg_date)
    if "§" in func_str:
        funcargs = func_str.split('§')
        return apply_fct(row, funcargs, func_str)
    return map_value(row, func_str)

def add_subfield(element_field, row, code, func_str, is_datafield=True):
    mapped_value = convert_field_content(row, func_str)
    if mapped_value == None or mapped_value == '' or str(mapped_value).lower() == 'nan':
        return None
    if is_datafield:
        subel = ET.SubElement(element_field, 'subfield', attrib={'code': code})
    else:
        subel = ET.SubElement(element_field, code)
    subel.text = rpl_json_spe_caracter(mapped_value)
    return subel

def create_datafield(tag_ind):
    match = re.search('([0-9]{3})(([0-9_])([0-9_]))?', tag_ind)
    tag = match.group(1)
    ind1 = get_ind(match.group(3))
    ind2 = get_ind(match.group(4))
    datafield = ET.Element('datafield', attrib={'tag': tag, 'ind1': ind1, 'ind2': ind2})
    return datafield 

def message_erreur_for(tag, sf):
    print("ERREUR arguments pour tag {tag} dans sf {sf}")
    print("Lorsque 'for' est utilisé, il faut au moins 2 arguments, exemple : 'for§boucle§contenu boucle")
    print("Note boucle for avec dictionnaire python : pour utliser l'élément courant dans le contenu de la boucle, utiliser %s")
    print("Note boucle for avec fichier excel externe : pour utliser l'élément courant dans le contenu de la boucle, utiliser %s<nom colonne>%s")
    print("Note : il est possible d'ajouter une condition dans la boucle comme suit : for§boucle§if§condition§alors§sinon")

def for_eval_boucle(row, el_params):
    if type(el_params)!= str:
        return None 
    if el_params.startswith("for§"):
        boucle_type = 'py_dict'
    elif el_params.startswith("forExcel§") :
        boucle_type = 'excel'
    else:
        return None
    # exemple de sf avec for : ["a", "for§'@Langue'.split('/')§if§%s in #lang008.keys§#lang008[%s]"]
    # sf[1] = "for§'@Langue'.split('/')§if§%s in #lang008.keys§#lang008[%s]"
    split_el_param = el_params.split('§') # = "for", "'@Langue'.split('/')", "if", "%s in #lang008.keys§#lang008[%s]"
    boucle = split_el_param[1] # = '@Langue'.split('/')
    # eval boucle
    boucle_eval = map_value(row, boucle, cond_var=True, cond_glob=True) # = 'EN/FR/DE'.split('/')
    # cette boucle permet de créer plusieurs sous-champs avec le même code en bouclant sur une liste
    # exemple : 041 $a eng $a fre $a ger
    return boucle_eval, split_el_param, boucle_type

def for_erreur(el_name, sf1_list, sf):
    if len(sf1_list)<2:
        message_erreur_for(el_name, sf)
        exit()

def convert_excel_val(excel_element, params_boucle):
    # Remplace valeur fichier dans condition
    # params_list = ["if", "%sIDJeux%s == @IDJeux"]
    func_arg = []
    for index, arg in enumerate(params_boucle):
        if index == 0:
            func_arg.append(arg)
            continue
        pattern = "%s([A-Z-a-z0-9_]+)%s"
        list_el_to_replace = re.findall(pattern, arg)
        if list_el_to_replace == []:
            continue
        for el_to_replace in list_el_to_replace:
            match = re.search(pattern, arg)
            val = str(excel_element[match.group(1)]).strip()
            # Condition
            if index == 1:
                arg = arg.replace(match.group(), f"'{val}'")
            # valTrue et valFalse
            else:
                arg = arg.replace(match.group(), val)
        func_arg.append(arg)
    func_str = "§".join(func_arg)
    return func_str

def convert_py_dic_val(py_dic_el, params_boucle):
    func_arg = []
    for index, arg in enumerate(params_boucle):
        if index == 0:
            func_arg.append(arg)
            continue
        pattern = "%s"
        arg = arg.replace(pattern, f"'{py_dic_el}'")
        func_arg.append(arg)
    func_str = "§".join(func_arg)
    return func_str

def boucle_excel(row, boucle_eval, split_el_param, boucle_type, el_name, field, element_field, is_sf=True, stop_to_match=False):
    if boucle_type != 'excel':
        return
    for _, el in eval(boucle_eval):
        if el.all() == None:
            continue
        for_erreur(el_name, split_el_param, field)

        if is_sf:
            # convertir valeurs %s<col name>%s avec val excel file
            func_str = convert_excel_val(el, split_el_param[2:])             
            subfield = add_subfield(element_field, row, field[0], func_str)
            if subfield != None and stop_to_match:
                return subfield
        else:
            datafield = create_datafield(field[0])
            # reconstruction datafield avec ajout if et condition datafield
            list_of_sf_list = []
            for sf in field[2:]:
                if sf[0] == "_comment":
                    continue
                code = sf[0]
                valsf = sf[1]
                sf_split_el = [split_el_param[2], split_el_param[3], valsf]
                # convertir valeurs %s<col name>%s avec val excel file
                func_str = convert_excel_val(el, sf_split_el)
                sf_construct = [code, func_str]
                list_of_sf_list.append(sf_construct)
            subfields = create_subfield(row, datafield, list_of_sf_list, stop_to_match=True)
            if subfields != []:
                element_field.append(datafield)

def boucle_py_dict(row, boucle_eval, split_el_param, boucle_type, el_name, field, element_field, is_sf=True, stop_to_match=False):
    if boucle_type != 'py_dict':
        return
    for el in eval(boucle_eval):
        if el == None or el == '':
            continue
        for_erreur(el_name, split_el_param, field)

        if is_sf:
            func_str = convert_py_dic_val(el, split_el_param[2:])
            #func_str = "§".join(split_el_param[2:])
            subfield = add_subfield(element_field, row, field[0], func_str.replace("%s", f"'{el}'"))
            if subfield != None and stop_to_match:
                return subfield
        else:
            datafield = create_datafield(field[0])
            # reconstruction datafield avec ajout if et condition datafield
            list_of_sf_list = []
            for sf in field[2:]:
                if sf[0] == "_comment":
                    continue
                code = sf[0]
                valsf = sf[1]
                sf_split_el = [split_el_param[2], split_el_param[3], valsf]
                # convertir valeurs %s avec val py dict
                func_str = convert_py_dic_val(el, sf_split_el)
                #func_str = "§".join(sf_split_el)
                sf_construct = [code, func_str]
                list_of_sf_list.append(sf_construct)
            subfields = create_subfield(row, datafield, list_of_sf_list, stop_to_match=True)
            if subfields != []:
                element_field.append(datafield)
        """
        sf = field
        func_str = "§".join(split_el_param[2:])
        if is_sf:
            subfield = add_subfield(element_field, row, sf[0], func_str.replace("%s", f"'{el}'"))
        else:
            datafield = create_datafield(sf[0])
            subfield = create_subfield(row, datafield, sf)"""

def create_subfield(row, element_field, list_of_sf_list, is_datafield=True, stop_to_match=False):
    subfields = []
    for sf in list_of_sf_list:
        if sf[0] == "_comment":
            continue
        if is_datafield:
            el_name = element_field.attrib['tag']
        else :
            el_name = element_field.tag

        is_boucle = for_eval_boucle(row, sf[1])
        # si pas de boucle
        if not is_boucle:
            subfield = add_subfield(element_field, row, sf[0], sf[1], is_datafield=is_datafield)
            if subfield != None:
                subfields.append(subfield)
        else:
            boucle_eval = is_boucle[0]
            sf1_list = is_boucle[1]
            boucle_type = is_boucle[2]

            # gestion excel file
            subfield_excel = boucle_excel(row, boucle_eval, sf1_list, boucle_type, el_name, sf, element_field, stop_to_match=stop_to_match)
            if subfield_excel != None:
                subfields.append(subfield_excel)
            # gestion cas standards
            subfield_py_dict = boucle_py_dict(row, boucle_eval, sf1_list, boucle_type, el_name, sf, element_field, stop_to_match=stop_to_match)
            if subfield_py_dict != None:
                subfields.append(subfield_py_dict)
    return subfields