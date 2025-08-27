# ExcelMarc Bridge

## About

### EN
This project is a Python script that converts an .xlsx file into a MARC21/XML format ready to be uploaded into the Alma ILS. Each line of the input file is converted to a <record> that can optionally include holding and item data. A JSON parameter file defines the mapping between the input file’s columns and the MARC21 fields. The configuration also supports conditions, loops, and conversion keys to control how data is generated for each MARC subfield.

### FR
Ce projet est un script python qui permet de convertir un fichier .xlsx dans un format Marc21/xml prêt à charger sur le SIGB Alma. Chaque ligne du fichier d'entrée est convertie en <record> qui peut optionnellement inclure les données de holding et d'item. Un fichier de paramètres JSON permet de définir la correspondance entre les colonnes du fichier d'entrée et les balises du format Marc21. Il est possible de renseigner dans les paramètres des conditions, des boucles ainsi que des clés de conversion pour les données de chaque sous-champs MARC.

* Author: Noémie Payot (noemie.payot@bcu.unil.ch)
* Year: 2025
* Version: 1.0
* License: GNU General Public License v3.0

## Documentation

### Dependencies

* pandas
* xml.etree.ElementTree
* re
* datetime
* string

### Installation

* Clone the repository to your machine.
* Copy gen_params_default.json, rename it to gen_params.json, and set the configuration variables.
* run main_vX.py

### Configuration

Configuration of gen_params.json file

#### General sections

* xlsx_file_input: input file name without extension
* xml_file_output: output file name without extension
* xlsx_folder: name of the subfolder containing any additional Excel files
* global_dict: If the data in certain columns needs to be mapped according to a list of values, these can be added here in the form of Python dictionaries: key = value from the Excel file, value = output value.

Dictionary example:
```
"conv_age": {
    "0.5": "6 months",
    "1.5": "18 months",
    "2.5": "2 years and 6 months"
},
```
* mapping : Add each field and subfield to be created here in list form. 
The first element in the list may contain one of the following terms:
* mmsid
* leader
* holding_data
* item_data
It may also contain the tag of a controlfield or datafield (e.g., "245"; indicators may be added optionally, e.g., "0243_").

Mmsid and leader can only be followed by a string. Other elements are followed by lists.

Leader example:
```
["leader", "02167nrm a2200457 a 4500"]
```
Controlfield example:
```
["007",
    ["pos0-5", "k|||m|"]
]
```
Datafield example:
```
["0243_",
    ["a", "@EAN13"]
],
```
Holding data example:
```
["holding_data",
    ["leader", "     nx  a22     1n 4500"],
    ["852",
        ["b", "#codes_bib['code_bib_alma']"],
        ["c", "@Localisation"],
        ["h", "@ESAR_secondaire"]
    ]
],
```
Item data example:
```
["item_data",
    ["barcode", "EY@Numero_jeu"],
    ["physical_material_type", "VIDEOGAME"],
    ["policy", "3000"]
]
```
Any list or sublist beginning with "_comment" is ignored.
The complete list of data for items is available here: https://developers.exlibrisgroup.com/alma/apis/docs/xsd/rest_item.xsd/?tags=PUT#item_data

#### Note for developers
Eval function (https://docs.python.org/3/library/functions.html#eval) is used on the second element of sublists, so any standard Python functions may be used.

#### Add fixed value
By default, the second element in the list is considered as a fixed value.
E.g. ["physical_material_type", "VIDEOGAME"]


#### Use column name
To include the value of a column in the field, add the column name preceded by @.
E.g. "@Title /" adds the title followed by a slash.

#### Mapping value with Python dict
Use dictionary name and key preceded by #.
E.g. "#codes_bib['indice_classification']"

#### Conditions
To inclue condition, the second element in the list must begin with "if§Condition§True value§Optional false value."
The § character is a delimiter between the different elements.
It is possible to include intermediate conditions. In this case, it is necessary to add several lists.
For example:
```
["500",
    ["a", "if§'0' == @Age_min§"],
    ["a", "elif§re.search('^[0-9]+$', @Age_min)§Min. age: @Age_min years"],
    ["a", "elif§re.search('^[012].5$', @Age_min)§Min. age: #conv_age[@Age_min]"]
],
```
In this example, if the variable @Age is 0, no value is added. Otherwise, if the variable contains one or more digits between 0 and 9 (see documentation on re.search : https://docs.python.org/3/library/re.html#re.search), the value "Min. age: <Age colunm value> years" is added. Otherwise, if the variable contains 0, 1, or 2 followed by .5, the value "Min. age: <value from the Python dictionary conv_age>" is added.
In this example, no value is added if none of the conditions are met.

#### Add and convert date format
##### Convert existing date
To convert the date format, use format_date(date to convert, input date format, output date format)
E.g.: ["inventory_date", "format_date(@Date_modif, %Y-%m-%d %H:%M:%S, %Y-%m-%d)"]

##### Add today date
Use today_date(output date format)
E.g: ["b", "today_date(%y%m)"]

##### Note
List of common date formats
* %d - Day of the month as a zero-padded decimal number. E.g. 01, 02, …, 31
* %m - Month as a zero-padded decimal number. E.g. 01, 02, …, 12
* %y - Year without century as a zero-padded decimal number. E.g. 00, 01, …, 99
* %Y - Year with century as a decimal number. E.g. 0001, 0002, …, 2013, 2014, …, 9998, 9999
* %H - Hour (24-hour clock) as a zero-padded decimal number.
* %M - Minute as a zero-padded decimal number. E.g. 00, 01, …, 59
* %S - Second as a zero-padded decimal number. E.g. 00, 01, …, 59

Function strftime is used
See docuemntation : https://docs.python.org/3/library/datetime.html

#### Loops with external Excel file
It is possible to add data from multiple Excel files. For example, if the authors are in a separate file and there may be several authors for the same record, it is possible to add a data field for each author.

Main file:
```
IdMain | Title |...
001 | My title | ...
```
Author file:
```
IdAut | Role | Name
001 | ill | Name1, FirstName1
001 | oth | Name2, FisteName2
```
Mapping data:
```
["700", "forExcel§#auteurs_liste.iterrows()§if§%sIdAut%s == @IdMain",
    ["a", "%sAuteurs_Nom%s, %sAuteurs_Prenom%s"],
    ["4", "%sRole%s"]
]
```
Output data:
```
<record>
    <datafield tag="035" ind1="1" ind2=" ">
        <subfield code="a">(TEST)001</subfield>
    </datafield>

    <datafield tag="700" ind1="1" ind2=" ">
        <subfield code="a">Name1, Firstname1</subfield>
        <subfield code="4">ill</subfield>
    </datafield>
        <datafield tag="700" ind1="1" ind2=" ">
        <subfield code="a">Name2, Fistname2</subfield>
        <subfield code="4">oth</subfield>
    </datafield>
    ...
</record>
```

To link files, Excel loop may be used and the second element in the list must begin with "forExcel§filename.iterrows()§Condition§True value§Optional false value."
The § character is a delimiter between the different elements.
%sCurrent element%s is column name of author file.

In the previous example :
```
["700", "forExcel§#auteurs_liste.iterrows()§if§%sIdAut%s == @IdMain",
    ["a", "%sAuteurs_Nom%s, %sAuteurs_Prenom%s"],
    ["4", "%sRole%s"]
]
```
For each row in the author Excel file, if the current IdAut equals Id of main file, add subfield a with name and subfield 4 with role

#### Loops with Python dict
To inclue loop, the second element in the list must begin with "for§Loop element§Condition§True value§Optional false value."
The § character is a delimiter between the different elements.
%s is the current loop element.

Example :
Python dictionary:
```
"lang008": {
    "EN": "eng",
    "FR": "fre",
    "DE": "ger",
    "ES": "spa",
    "IT": "ita",
    "NL": "dut",
    "PT": "por"
}
```
Mapping value:
```
["041",
    ["a", "for§@Langue.split('/')§if§%s in #lang008.keys()§#lang008[%s]"]
]
```
Value of Langue column in Excel file:
```
EN/FR/DE
```
Output value:
```
<datafield tag="041" ind1=" " ind2=" ">
    <subfield code="a">eng</subfield>
    <subfield code="a">fre</subfield>
    <subfield code="a">ger</subfield>
</datafield>
```
In this example, multiple subfields 'a' are added in one 041 datafield.
The value of the column is split at each slash (see documentation on split : https://docs.python.org/3.10/library/stdtypes.html#str.split) and for each of these values ('EN', 'FR' and 'DE'), if the condition is met = if the current value is found among the keys in the lang008 dictionary, a subfield is added with corresponding key value.


