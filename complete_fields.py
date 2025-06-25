""" Python libraries """
from cmath import nan
from multiprocessing import Value
import xml.etree.ElementTree as ET
import re
from datetime import datetime

""" Local functions """
import global_dict

def rpl_json_spe_caracter(ET_el):
    ET_el = ET_el.replace("<diese>", "#")
    ET_el = ET_el.replace("<at>", "@")
    return ET_el

def get_ind(check_str):
    if check_str != None:
        return check_str.replace("_", " ")
    return ' '

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
            """if col_name == "Age_min" and "5" in col_val:
                print(col_val)
                breakpoint()"""
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
        breakpoint()

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
    if "0,5" in condition:
        breakpoint()
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
    m_format_date = re.search(f"foramt_date\((@[a-zA-Z0-9]+), ({reg_date}), ({reg_date})\)", content)
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
            reg_date = "[%abdHMSZYm\.\-:_ ]+"
            if fct_date == "format_date":
                func_str = fct_format_date(row, func_str, reg_date)
            elif fct_date == "today_date":
                func_str = fct_today_date(func_str, reg_date)
    if "§" in func_str:
        funcargs = func_str.split('§')
        return apply_fct(row, funcargs, func_str)
    return map_value(row, func_str)

def add_subfield(datafield, row, code, func_str):
    subfield = ET.SubElement(datafield, 'subfield', attrib={'code': code})
    subfield.text = convert_field_content(row, func_str)
    subfield.text = rpl_json_spe_caracter(subfield.text)

def message_erreur_for(tag, sf):
    print("ERREUR arguments pour tag {tag} dans sf {sf}")
    print("Lorsque 'for' est utilisé, il faut au moins 2 arguments, exemple : 'for§boucle§contenu boucle")
    print("Note : pour utliser l'élément courant dans le contenu de la boucle, utiliser %s")
    print("Note : il est possible d'ajouter une condition dans la boucle comme suit : for§boucle§if§condition§alors§sinon")