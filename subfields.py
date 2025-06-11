import xml.etree.ElementTree as ET


def marc_subfield(tag, code, value):
    datafield = ET.Element('datafield', attrib={'tag': tag, 'ind1': ' ', 'ind2': ' '})
    subfield = ET.SubElement(datafield, 'subfield', attrib={'code': code})
    subfield.text = value
    return datafield